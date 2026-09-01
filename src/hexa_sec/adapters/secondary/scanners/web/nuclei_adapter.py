"""NucleiAdapter — a Dockerized web tool (context: web)."""

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

_TOOL = "web_cve_templates_nuclei"


class NucleiAdapter(WebScannerPort):
    """Run ``nuclei -u <asset>`` via the shared Docker runtime and parse JSON."""

    def __init__(self, execution: ToolExecutionPort, image_policy: ImagePolicy) -> None:
        self._execution = execution
        self._image_policy = image_policy

    def scan(self, asset: str) -> list[WebFindingRecord]:
        image = self._image_policy.resolve(_TOOL)
        if image is None:
            raise ScannerUnavailableError("nuclei image is not approved")
        request = ToolExecutionRequest(
            image=image.image,
            digest=image.digest,
            command="nuclei",
            tool=_TOOL,
            arguments=("-u", asset, "-json"),
            network="bridge",
            resources=ResourceLimits(memory_mb=512, pids=256),
            timeout=180.0,
            execution_id=f"nuclei-{asset}",
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
        items: list[object] = raw if isinstance(raw, list) else [raw]
        for item in items:
            if not isinstance(item, dict):
                continue
            info = item.get("info", {}) if isinstance(item.get("info"), dict) else {}
            records.append(
                WebFindingRecord(
                    title=str(info.get("name", "nuclei finding")),
                    severity=str(info.get("severity", "info")),
                    url=str(item.get("host", "")),
                )
            )
        return records
