"""ContainerFinding — a container image vulnerability (context: container_risk).

A CVE found in a container image, with its computed severity. The image and the
severity are validated and the CVE is normalized (uppercase) — never guessed.
"""

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
        if not isinstance(self.image, ImageRef):
            raise ValueError("container finding image must be an ImageRef")
        if not self.cve or not self.cve.strip():
            raise ValueError("container finding cve cannot be empty")
        if not isinstance(self.severity, Severity):
            raise ValueError("container finding severity must be a Severity")
        object.__setattr__(self, "cve", self.cve.strip().upper())

    def severe(self) -> bool:
        """Whether the finding is HIGH or CRITICAL."""
        return self.severity in (Severity.HIGH, Severity.CRITICAL)
