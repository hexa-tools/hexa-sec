"""ConfigRisk — the consolidated config-deviation inventory (context: config_risk, SEC-15).

``for_asset`` groups findings under an asset and deduplicates by
(asset, benchmark, check): two distinct checks stay separate (never merged), a
tolerable (low-severity) gap is kept, never silently dropped. On a duplicate the
highest severity wins, then the smallest evidence — deterministic, independent of
arrival order.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.config_risk.config_finding import ConfigFinding
from hexa_sec.domain.finding.severity import Severity


@dataclass(frozen=True)
class ConfigRisk:
    """The inventory of config findings for a single asset."""

    asset: str
    findings: tuple[ConfigFinding, ...]

    @property
    def gap_count(self) -> int:
        """Number of configuration gaps."""
        return len(self.findings)

    @property
    def critical_count(self) -> int:
        """Number of findings at CRITICAL severity."""
        return sum(1 for finding in self.findings if finding.severity is Severity.CRITICAL)

    @classmethod
    def for_asset(cls, asset: str, findings: Iterable[ConfigFinding]) -> ConfigRisk:
        """Build a consolidated inventory, deduplicated by (asset, benchmark, check)."""
        seen: dict[tuple[str, str, str], ConfigFinding] = {}
        for finding in findings:
            if finding.asset != asset:
                continue
            key = (finding.asset, finding.benchmark_id.identifier, finding.check.identifier)
            existing = seen.get(key)
            if existing is None or _prefer(finding, existing):
                seen[key] = finding
        return cls(asset=asset, findings=tuple(seen.values()))


def _prefer(candidate: ConfigFinding, current: ConfigFinding) -> bool:
    """Whether ``candidate`` should replace ``current`` for the same key.

    The highest severity wins; on a severity tie the smallest evidence wins.
    This total order makes the consolidation independent of arrival order.
    """
    if candidate.severity.rank != current.severity.rank:
        return candidate.severity.rank > current.severity.rank
    return candidate.evidence < current.evidence
