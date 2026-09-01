"""IdentityFinding — an identity/access issue (context: identity_risk, SEC-19).

An adapter (bloodhound/crackmapexec/impacket) translates a scanner hit into an
IdentityFinding: the Principal, the issue, its AccessRisk, the Severity and the
evidence. The severity must respect the access-risk floor — a PRIVILEGED account
is never LOW — and the evidence is mandatory (no invented issue).
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.identity_risk.access_risk import AccessRisk
from hexa_sec.domain.identity_risk.principal import Principal


@dataclass(frozen=True)
class IdentityFinding:
    """A single identity/access risk."""

    principal: Principal
    issue: str
    access_risk: AccessRisk
    severity: Severity
    evidence: str

    def __post_init__(self) -> None:
        if not isinstance(self.principal, Principal):
            raise ValueError("identity finding principal must be a Principal")
        if not self.issue or not self.issue.strip():
            raise ValueError("identity finding issue cannot be empty")
        if not isinstance(self.access_risk, AccessRisk):
            raise ValueError("identity finding access_risk must be an AccessRisk")
        if not isinstance(self.severity, Severity):
            raise ValueError("identity finding severity must be a Severity")
        if not self.evidence or not self.evidence.strip():
            raise ValueError("identity finding requires evidence (proof)")
        if self.severity.rank < self.access_risk.min_severity().rank:
            raise ValueError(
                f"identity finding severity too low for {self.access_risk.value} "
                "(privileged account must be at least HIGH)"
            )
        object.__setattr__(self, "issue", self.issue.strip())
