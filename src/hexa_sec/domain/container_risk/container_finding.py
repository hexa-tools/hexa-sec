"""ContainerFinding — a container image vulnerability (context: container_risk)."""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.container_risk.image_ref import ImageRef
from hexa_sec.domain.finding.severity import Severity


@dataclass(frozen=True)
class ContainerFinding:
    """A CVE found in a container image."""

    image: ImageRef
    cve: str
    severity: Severity = Severity.MEDIUM

    def __post_init__(self) -> None:
        if not self.cve.strip():
            raise ValueError("container finding cve cannot be empty")

    def severe(self) -> bool:
        return self.severity in (Severity.HIGH, Severity.CRITICAL)
