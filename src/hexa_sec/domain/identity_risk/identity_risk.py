"""IdentityRisk — the consolidated identity/access inventory (context: identity_risk, SEC-19).

``for_principal`` groups findings under a principal and deduplicates by
(principal, issue, access_risk): distinct issues stay separate, a technical
account (low severity) is kept — never silently dropped. On a duplicate the
highest severity wins, then the smallest evidence — deterministic, independent
of arrival order.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.identity_risk.access_risk import AccessRisk
from hexa_sec.domain.identity_risk.identity_finding import IdentityFinding


@dataclass(frozen=True)
class IdentityRisk:
    """The inventory of identity findings for a single principal."""

    principal: str
    findings: tuple[IdentityFinding, ...]

    @property
    def risk_count(self) -> int:
        """Number of identity findings."""
        return len(self.findings)

    @property
    def privileged_count(self) -> int:
        """Number of findings classified as PRIVILEGED."""
        return sum(1 for finding in self.findings if finding.access_risk is AccessRisk.PRIVILEGED)

    @classmethod
    def for_principal(cls, principal: str, findings: Iterable[IdentityFinding]) -> IdentityRisk:
        """Build a consolidated inventory, deduplicated by (principal, issue, access_risk)."""
        normalized = principal.strip()
        if not normalized:
            raise ValueError("identity principal cannot be empty")
        seen: dict[tuple[str, str, str], IdentityFinding] = {}
        for finding in findings:
            if finding.principal.value != normalized:
                continue
            key = (finding.principal.value, finding.issue, finding.access_risk.value)
            existing = seen.get(key)
            if existing is None or _prefer(finding, existing):
                seen[key] = finding
        return cls(principal=normalized, findings=tuple(seen.values()))


def _prefer(candidate: IdentityFinding, current: IdentityFinding) -> bool:
    """Whether ``candidate`` should replace ``current`` for the same key.

    The highest severity wins; on a severity tie the smallest evidence wins.
    This total order makes the consolidation independent of arrival order.
    """
    if candidate.severity.rank != current.severity.rank:
        return candidate.severity.rank > current.severity.rank
    return candidate.evidence < current.evidence
