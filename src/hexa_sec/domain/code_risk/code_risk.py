"""CodeRisk — the consolidated static-code inventory (context: code_risk, SEC-14).

``for_asset`` groups findings under an asset and deduplicates by
(asset, rule, file, line): the same rule at two locations stays two findings
(never merged), and a low-severity benign pattern is kept, never silently
dropped. On a duplicate the highest severity wins — deterministic, independent
of arrival order.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.code_risk.code_finding import CodeFinding
from hexa_sec.domain.finding.severity import Severity


@dataclass(frozen=True)
class CodeRisk:
    """The inventory of static-code findings for a single asset."""

    asset: str
    findings: tuple[CodeFinding, ...]

    @property
    def risk_count(self) -> int:
        """Number of static-code findings."""
        return len(self.findings)

    @property
    def critical_count(self) -> int:
        """Number of findings at CRITICAL severity."""
        return sum(1 for finding in self.findings if finding.severity is Severity.CRITICAL)

    @classmethod
    def for_asset(cls, asset: str, findings: Iterable[CodeFinding]) -> CodeRisk:
        """Build a consolidated inventory, deduplicated by (asset, rule, file, line)."""
        seen: dict[tuple[str, str, str, int], CodeFinding] = {}
        for finding in findings:
            if finding.asset != asset:
                continue
            key = (
                finding.asset,
                finding.rule_id.identifier,
                finding.location.file,
                finding.location.line,
            )
            existing = seen.get(key)
            if existing is None or _prefer(finding, existing):
                seen[key] = finding
        return cls(asset=asset, findings=tuple(seen.values()))


def _prefer(candidate: CodeFinding, current: CodeFinding) -> bool:
    """Whether ``candidate`` should replace ``current`` for the same key.

    The highest severity wins; on a severity tie the smallest evidence wins.
    This total order makes the consolidation independent of arrival order.
    """
    if candidate.severity.rank != current.severity.rank:
        return candidate.severity.rank > current.severity.rank
    return candidate.evidence < current.evidence
