"""ZapAdapter — a Dockerized web tool (context: web, tool web_vuln_scan_zap).

Mirrors ``nuclei_adapter.py``: the adapter resolves an approved image, runs
the tool through the shared :class:`ToolExecutionPort` and normalizes the
ZAP JSON report (Automation Framework) into :class:`WebFindingRecord`.

The ``web_vuln_scan_zap`` image (``zaproxy/zap-stable``) is already declared in
``packs/scanners.yml``; its digest is pinned by an operator at Docker
integration time. The adapter never bypasses the mandate gate enforced by
``scan_asset`` and never invents a severity the scanner did not state.
"""

from __future__ import annotations

import json

from hexa_sec.application.ports.driven.execution_port import (
    ResourceLimits,
    ToolExecutionPort,
    ToolExecutionRequest,
)
from hexa_sec.application.ports.driven.image_policy import ImagePolicy
from hexa_sec.application.ports.driven.web_scanner_port import WebFindingRecord, WebScannerPort
from hexa_sec.domain.errors import ScannerUnavailableError

_TOOL = "web_vuln_scan_zap"

_RISKCODE_TO_SEVERITY: dict[str, str] = {
    "0": "info",
    "1": "low",
    "2": "medium",
    "3": "high",
}

_RISK_TO_SEVERITY: dict[str, str] = {
    "informational": "info",
    "info": "info",
    "low": "low",
    "medium": "medium",
    "high": "high",
    "critical": "critical",
}


def _severity_from(riskcode: object, risk: object) -> str:
    """Map ZAP ``riskcode`` (0-3) then ``risk`` onto the shared vocabulary.

    The numeric code is authoritative when it parses; otherwise the label is
    used. Unknown and absent labels both fall back to ``info``: never invent a
    severity the scanner did not state.
    """
    if isinstance(riskcode, (int, str)):
        code = str(riskcode).strip()
        mapped = _RISKCODE_TO_SEVERITY.get(code)
        if mapped is not None:
            return mapped
    if isinstance(risk, str) and risk.strip():
        return _RISK_TO_SEVERITY.get(risk.strip().lower(), "info")
    return "info"


class ZapAdapter(WebScannerPort):
    """Run ZAP against an asset and normalize its JSON report to findings."""

    def __init__(self, execution: ToolExecutionPort, image_policy: ImagePolicy) -> None:
        self._execution = execution
        self._image_policy = image_policy

    def scan(self, asset: str) -> list[WebFindingRecord]:
        image = self._image_policy.resolve(_TOOL)
        if image is None:
            raise ScannerUnavailableError(f"{_TOOL} image is not approved")
        request = ToolExecutionRequest(
            image=image.image,
            digest=image.digest,
            command="zap",
            tool=_TOOL,
            arguments=("-u", asset, "--json"),
            network="bridge",
            resources=ResourceLimits(memory_mb=512, pids=256),
            timeout=180.0,
            execution_id=f"zap-{asset}",
        )
        result = self._execution.execute(request)
        return self._parse(result.stdout)

    @staticmethod
    def _parse(output: str) -> list[WebFindingRecord]:
        records: list[WebFindingRecord] = []
        if not output.strip():
            return records
        try:
            raw = json.loads(output)
        except json.JSONDecodeError:
            return records
        if not isinstance(raw, dict):
            return records
        sites = raw.get("site")
        if not isinstance(sites, list):
            return records
        for site in sites:
            if not isinstance(site, dict):
                continue
            alerts = site.get("alerts")
            if not isinstance(alerts, list):
                continue
            for alert in alerts:
                if not isinstance(alert, dict):
                    continue
                title = alert.get("alert")
                url = alert.get("url")
                if not isinstance(title, str) or not title.strip():
                    continue
                if not isinstance(url, str) or not url.strip():
                    continue
                records.append(
                    WebFindingRecord(
                        title=title.strip(),
                        severity=_severity_from(alert.get("riskcode"), alert.get("risk")),
                        url=url.strip(),
                    )
                )
        return records
