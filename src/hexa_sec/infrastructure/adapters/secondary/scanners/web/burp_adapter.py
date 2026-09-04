"""BurpAdapter — a Dockerized web tool (context: web, tool web_vuln_scan_burp).

Mirrors ``nuclei_adapter.py``: the adapter resolves an approved image, runs
the tool through the shared :class:`ToolExecutionPort` and normalizes the
Burp issues-export JSON into :class:`WebFindingRecord`.

Deny-by-default: Burp Suite Pro has no official headless image, so the entry
in ``packs/scanners.yml`` deliberately carries no image yet. Until an operator
approves an image+digest, ``ImagePolicy.resolve`` returns ``None`` and the scan
raises :class:`ScannerUnavailableError` — the adapter never runs unapproved
tooling, and it never bypasses the mandate gate enforced by ``scan_asset``.
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

_TOOL = "web_vuln_scan_burp"

_SEVERITY_MAP: dict[str, str] = {
    "info": "info",
    "information": "info",
    "informational": "info",
    "low": "low",
    "medium": "medium",
    "high": "high",
    "critical": "critical",
}


def _normalized_severity(raw: object) -> str:
    """Map a Burp severity label onto the shared info..critical vocabulary.

    Unknown labels fall back to ``info``: never invent a severity the scanner
    did not state. A missing/blank severity is an absence, not a level.
    """
    if isinstance(raw, str) and raw.strip():
        return _SEVERITY_MAP.get(raw.strip().lower(), "info")
    return "info"


class BurpAdapter(WebScannerPort):
    """Run Burp against an asset and normalize its issues export to findings."""

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
            command="burp",
            tool=_TOOL,
            arguments=("-u", asset, "--json"),
            network="bridge",
            resources=ResourceLimits(memory_mb=512, pids=256),
            timeout=180.0,
            execution_id=f"burp-{asset}",
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
        issues: object
        if isinstance(raw, dict):
            issues = raw.get("issues")
        elif isinstance(raw, list):
            issues = raw
        else:
            return records
        if not isinstance(issues, list):
            return records
        for item in issues:
            if not isinstance(item, dict):
                continue
            title = item.get("name")
            host = item.get("host")
            if not isinstance(title, str) or not title.strip():
                continue
            if not isinstance(host, str) or not host.strip():
                continue
            path = item.get("path")
            url = host
            if isinstance(path, str) and path.strip():
                url = f"{host}{path.strip()}"
            records.append(
                WebFindingRecord(
                    title=title.strip(),
                    severity=_normalized_severity(item.get("severity")),
                    url=url,
                )
            )
        return records
