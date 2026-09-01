"""EmailRisk — the consolidated email-spoofing inventory (context: email_risk).

``of`` deduplicates findings by domain (keeping the worst DMARC posture) and
sorts deterministically. Nothing raises when a domain is not spoofable or none
is present.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.email_risk.dmarc_status import DmarcStatus
from hexa_sec.domain.email_risk.email_finding import EmailFinding


@dataclass(frozen=True)
class EmailRisk:
    """The email findings of the audited domains."""

    findings: tuple[EmailFinding, ...]

    @property
    def spoofable_count(self) -> int:
        """Number of domains that can be spoofed."""
        return sum(1 for finding in self.findings if finding.spoofable())

    def spoofable_domains(self) -> tuple[str, ...]:
        """The domains that can be spoofed, sorted."""
        return tuple(sorted(finding.domain for finding in self.findings if finding.spoofable()))

    @classmethod
    def of(cls, findings: Iterable[EmailFinding]) -> EmailRisk:
        """Build the inventory, deduplicated by domain (worst DMARC kept)."""
        seen: dict[str, EmailFinding] = {}
        for finding in findings:
            existing = seen.get(finding.domain)
            if existing is None or _prefer(finding, existing):
                seen[finding.domain] = finding
        return cls(tuple(sorted(seen.values(), key=lambda f: f.domain)))


def _dmarc_rank(status: DmarcStatus) -> int:
    """Higher = worse posture (more spoofable)."""

    return {
        DmarcStatus.MISSING: 3,
        DmarcStatus.NONE: 2,
        DmarcStatus.QUARANTINE: 1,
        DmarcStatus.REJECT: 0,
    }[status]


def _prefer(candidate: EmailFinding, current: EmailFinding) -> bool:
    """Whether ``candidate`` should replace ``current`` for the same domain."""
    return _dmarc_rank(candidate.dmarc) > _dmarc_rank(current.dmarc)
