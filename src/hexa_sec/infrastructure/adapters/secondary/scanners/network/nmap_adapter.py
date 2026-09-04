"""NmapAdapter — the reference Dockerized tool (context: network)."""

from __future__ import annotations

import re

from hexa_sec.application.ports.driven.execution_port import (
    ResourceLimits,
    ToolExecutionPort,
    ToolExecutionRequest,
)
from hexa_sec.application.ports.driven.image_policy import ImagePolicy
from hexa_sec.application.ports.driven.network_scanner_port import (
    NetworkFindingRecord,
    NetworkScannerPort,
)
from hexa_sec.domain.errors import ScannerUnavailableError

_TOOL = "network_port_discovery"
_PORT_LINE = re.compile(r"^(\d+)/tcp\s+open\s+(\S+)")


class NmapAdapter(NetworkScannerPort):
    """Run ``nmap -sV`` via the shared Docker runtime and parse open ports."""

    def __init__(self, execution: ToolExecutionPort, image_policy: ImagePolicy) -> None:
        self._execution = execution
        self._image_policy = image_policy

    def scan(self, asset: str) -> list[NetworkFindingRecord]:
        image = self._image_policy.resolve(_TOOL)
        if image is None:
            raise ScannerUnavailableError("nmap image is not approved")
        request = ToolExecutionRequest(
            image=image.image,
            digest=image.digest,
            command="nmap",
            tool=_TOOL,
            arguments=("-sV", asset),
            network="bridge",
            resources=ResourceLimits(memory_mb=512, pids=256),
            timeout=120.0,
            execution_id=f"nmap-{asset}",
        )
        result = self._execution.execute(request)
        return self._parse(result.stdout, asset)

    @staticmethod
    def _parse(output: str, asset: str) -> list[NetworkFindingRecord]:
        records: list[NetworkFindingRecord] = []
        for line in output.splitlines():
            match = _PORT_LINE.match(line.strip())
            if match:
                records.append(
                    NetworkFindingRecord(
                        host=asset,
                        port=int(match.group(1)),
                        service=match.group(2),
                    )
                )
        return records
