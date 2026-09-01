"""IaacRisk — the consolidated IaC inventory (context: iaac_risk, SEC-17).

``for_asset`` groups findings under an asset and deduplicates by
(resource_type, path): a resource already reported (even one since removed from
the repo) is traced once, never duplicated, and a low-severity finding is kept.
On a duplicate the highest severity wins, then the smallest evidence —
deterministic, independent of arrival order.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.iaac_risk.iaac_finding import IaacFinding


@dataclass(frozen=True)
class IaacRisk:
    """The inventory of IaC findings for a single asset."""

    asset: str
    findings: tuple[IaacFinding, ...]

    @property
    def risk_count(self) -> int:
        """Number of IaC findings."""
        return len(self.findings)

    @property
    def critical_count(self) -> int:
        """Number of findings at CRITICAL severity."""
        return sum(1 for finding in self.findings if finding.severity is Severity.CRITICAL)

    @classmethod
    def for_asset(cls, asset: str, findings: Iterable[IaacFinding]) -> IaacRisk:
        """Build a consolidated inventory, deduplicated by (resource_type, path)."""
        seen: dict[tuple[str, str], IaacFinding] = {}
        for finding in findings:
            key = (finding.resource_type.value, finding.path.path)
            existing = seen.get(key)
            if existing is None or _prefer(finding, existing):
                seen[key] = finding
        return cls(asset=asset, findings=tuple(seen.values()))


def _prefer(candidate: IaacFinding, current: IaacFinding) -> bool:
    """Whether ``candidate`` should replace ``current`` for the same key.

    The highest severity wins; on a severity tie the smallest evidence wins.
    This total order makes the consolidation independent of arrival order.
    """
    if candidate.severity.rank != current.severity.rank:
        return candidate.severity.rank > current.severity.rank
    return candidate.evidence < current.evidence
