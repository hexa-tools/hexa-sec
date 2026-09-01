"""ContainerRisk — the consolidated container-image inventory (context: container_risk).

``of`` deduplicates findings by (image, cve) keeping the highest severity, and
sorts deterministically. The same CVE in two images stays two findings (one per
image); nothing raises when no image is vulnerable.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.container_risk.container_finding import ContainerFinding


@dataclass(frozen=True)
class ContainerRisk:
    """The container findings of the audited images."""

    findings: tuple[ContainerFinding, ...]

    @property
    def vulnerable_count(self) -> int:
        """Number of image/CVE findings."""
        return len(self.findings)

    @property
    def severe_count(self) -> int:
        """Number of findings at HIGH/CRITICAL severity."""
        return sum(1 for finding in self.findings if finding.severe())

    def severe_images(self) -> tuple[str, ...]:
        """The qualified refs of images with a severe finding, sorted."""
        return tuple(sorted({f.image.qualified for f in self.findings if f.severe()}))

    @classmethod
    def of(cls, findings: Iterable[ContainerFinding]) -> ContainerRisk:
        """Build the inventory, deduplicated by (image, cve) (highest severity kept)."""
        seen: dict[tuple[str, str], ContainerFinding] = {}
        for finding in findings:
            key = (finding.image.qualified, finding.cve)
            existing = seen.get(key)
            if existing is None or finding.severity.rank > existing.severity.rank:
                seen[key] = finding
        return cls(tuple(sorted(seen.values(), key=lambda f: (f.image.qualified, f.cve))))
