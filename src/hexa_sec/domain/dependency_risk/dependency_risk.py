"""DependencyRisk — the consolidated vulnerable-dependency inventory.

``for_asset`` groups findings under an asset and deduplicates by
(package, version, CVE): the same package at two versions stays two findings
(never merged). It never raises when nothing is found — an empty inventory is
the normal answer, and finding construction already guarantees evidence (no
invented CVE reaches the inventory).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.dependency_risk.dependency import DependencyFinding
from hexa_sec.domain.finding.severity import Severity


@dataclass(frozen=True)
class DependencyRisk:
    """The inventory of vulnerable dependencies for a single asset."""

    asset: str
    findings: tuple[DependencyFinding, ...]

    @property
    def vulnerable_count(self) -> int:
        """Number of vulnerable-dependency findings."""
        return len(self.findings)

    @property
    def critical_count(self) -> int:
        """Number of findings at CRITICAL severity."""
        return sum(1 for finding in self.findings if finding.severity is Severity.CRITICAL)

    @classmethod
    def for_asset(cls, asset: str, findings: Iterable[DependencyFinding]) -> DependencyRisk:
        """Build a consolidated inventory, deduplicated by (package, version, CVE)."""
        seen: dict[tuple[str, str, str], DependencyFinding] = {}
        for finding in findings:
            key = (
                finding.dependency.package,
                finding.dependency.version,
                finding.cve,
            )
            existing = seen.get(key)
            if existing is None or finding.severity.rank > existing.severity.rank:
                seen[key] = finding
        return cls(asset=asset, findings=tuple(seen.values()))
