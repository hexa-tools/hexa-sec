"""ComplianceRisk — per-framework scoring, traced base (context: compliance, SEC-18).

``for_asset`` deduplicates the finding→scope links and scores every framework
0..100. A framework with no gaps is scored 100 (the base is traced, never
invented); gaps subtract a penalty by impact. The score and its level stay
coherent by construction. Nothing is guessed and nothing raises when a framework
is untouched.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.compliance.compliance_finding import ComplianceFinding
from hexa_sec.domain.compliance.compliance_scope import ComplianceScope
from hexa_sec.domain.compliance.compliance_score import ComplianceScore
from hexa_sec.domain.finding.severity import Severity

_PENALTY_BY_RANK = {0: 0, 1: 8, 2: 16, 3: 24, 4: 32}


@dataclass(frozen=True)
class ComplianceRisk:
    """The compliance posture of an asset across frameworks."""

    asset: str
    gaps: tuple[ComplianceFinding, ...]
    scores: tuple[ComplianceScore, ...]

    def non_compliant_scopes(self) -> tuple[ComplianceScope, ...]:
        """The frameworks currently failing (NON_COMPLIANT)."""
        return tuple(score.scope for score in self.scores if score.level().value == "non_compliant")

    @classmethod
    def for_asset(
        cls,
        asset: str,
        findings: Iterable[ComplianceFinding],
    ) -> ComplianceRisk:
        """Build the deduplicated gaps and the per-framework scores."""
        normalized_asset = asset.strip()
        if not normalized_asset:
            raise ValueError("compliance asset cannot be empty")
        gaps = _dedup(findings)
        scores = tuple(_score_scope(scope, gaps) for scope in ComplianceScope)
        return cls(asset=normalized_asset, gaps=gaps, scores=scores)


def _dedup(findings: Iterable[ComplianceFinding]) -> tuple[ComplianceFinding, ...]:
    """Keep the highest-impact link per (finding_id, scope), then order deterministically."""
    seen: dict[tuple[str, str], ComplianceFinding] = {}
    for finding in findings:
        key = (finding.finding_id.value, finding.scope.value)
        existing = seen.get(key)
        if existing is None or finding.impact.rank > existing.impact.rank:
            seen[key] = finding
    return tuple(sorted(seen.values(), key=lambda f: (f.scope.value, f.finding_id.value)))


def _penalty(impact: Severity) -> int:
    return _PENALTY_BY_RANK[impact.rank]


def _score_scope(scope: ComplianceScope, gaps: tuple[ComplianceFinding, ...]) -> ComplianceScore:
    penalty = sum(_penalty(gap.impact) for gap in gaps if gap.scope is scope)
    value = max(0, 100 - penalty)
    return ComplianceScore(scope=scope, value=value)
