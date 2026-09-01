"""CodeFinding — a risky static-code pattern (context: code_risk, SEC-14).

An adapter (semgrep/bandit) translates a scanner hit into a CodeFinding: the
asset, its RuleId, its CodeLocation, the Severity and the evidence. Without
evidence (location/preuve) there is no finding — no invented pattern.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.code_risk.code_location import CodeLocation
from hexa_sec.domain.code_risk.rule_id import RuleId
from hexa_sec.domain.finding.severity import Severity


@dataclass(frozen=True)
class CodeFinding:
    """A single risky code pattern detected in a repository."""

    asset: str
    rule_id: RuleId
    location: CodeLocation
    severity: Severity
    evidence: str

    def __post_init__(self) -> None:
        if not self.asset or not self.asset.strip():
            raise ValueError("code finding asset cannot be empty")
        if not isinstance(self.rule_id, RuleId):
            raise ValueError("code finding rule_id must be a RuleId")
        if not isinstance(self.location, CodeLocation):
            raise ValueError("code finding location must be a CodeLocation")
        if not isinstance(self.severity, Severity):
            raise ValueError("code finding severity must be a Severity")
        if not self.evidence or not self.evidence.strip():
            raise ValueError("code finding requires evidence (proof)")
