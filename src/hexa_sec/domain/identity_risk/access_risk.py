"""AccessRisk — the access-risk class of an identity (context: identity_risk, SEC-19).

The risk class of an AD/SSO account, and its imposed severity floor: a
PRIVILEGED account is at least HIGH — never LOW. Other classes (orphan,
excessive, technical account, normal) carry no imposed floor, so the scanner's
severity stands and a legitimate MEDIUM is never dropped.
"""

from __future__ import annotations

from enum import Enum

from hexa_sec.domain.finding.severity import Severity


class AccessRisk(Enum):
    """The access-risk class of an identity."""

    ORPHAN = "orphan"
    EXCESSIVE = "excessive"
    PRIVILEGED = "privileged"
    SERVICE = "service"
    NORMAL = "normal"

    def min_severity(self) -> Severity:
        """The minimum severity imposed by this access risk."""
        if self is AccessRisk.PRIVILEGED:
            return Severity.HIGH
        return Severity.LOW

    @classmethod
    def normalize(cls, raw: str) -> AccessRisk:
        """Map a raw label to an ``AccessRisk``; unknown values are rejected."""
        cleaned = raw.strip().lower()
        try:
            return cls(cleaned)
        except ValueError as error:
            raise ValueError(f"unknown access risk: {raw}") from error
