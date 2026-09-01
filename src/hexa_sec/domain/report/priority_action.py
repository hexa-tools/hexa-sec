"""PriorityAction — a « fix first » action (context: report)."""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.scoring.risk_score import RiskScore


@dataclass(frozen=True)
class PriorityAction:
    """What to fix first: the failing finding, why it matters, the fix, the effort."""

    finding_id: FindingId
    issue: str
    why: str
    fix: str
    effort: str
    risk_score: RiskScore

    def __post_init__(self) -> None:
        if self.finding_id is None:
            raise ValueError("priority action requires a source finding (no speculation)")
        for name in ("issue", "why", "fix", "effort"):
            if not getattr(self, name).strip():
                raise ValueError(f"priority action {name} cannot be empty")
