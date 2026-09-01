"""DnsRisk — the consolidated DNS exposure inventory (context: dns_risk).

``of`` deduplicates findings by domain (keeping the most severe posture) and
sorts deterministically. Nothing raises when a domain is not exposed or none is
present.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.dns_risk.dns_finding import DnsFinding


@dataclass(frozen=True)
class DnsRisk:
    """The DNS findings of the audited domains."""

    findings: tuple[DnsFinding, ...]

    @property
    def exposed_count(self) -> int:
        """Number of domains with at least one resolved subdomain."""
        return sum(1 for finding in self.findings if finding.exposed())

    @property
    def zone_transfer_count(self) -> int:
        """Number of domains allowing a zone transfer."""
        return sum(1 for finding in self.findings if finding.has_zone_transfer())

    def exposed_domains(self) -> tuple[str, ...]:
        """The exposed domains, sorted."""
        return tuple(sorted(finding.domain for finding in self.findings if finding.exposed()))

    @classmethod
    def of(cls, findings: Iterable[DnsFinding]) -> DnsRisk:
        """Build the inventory, deduplicated by domain (most severe kept)."""
        seen: dict[str, DnsFinding] = {}
        for finding in findings:
            existing = seen.get(finding.domain)
            if existing is None or _prefer(finding, existing):
                seen[finding.domain] = finding
        return cls(tuple(sorted(seen.values(), key=lambda f: f.domain)))


def _severity(finding: DnsFinding) -> tuple[int, int]:
    """(zone_transfer, exposed) — higher is worse."""
    return (int(finding.has_zone_transfer()), int(finding.exposed()))


def _prefer(candidate: DnsFinding, current: DnsFinding) -> bool:
    """Whether ``candidate`` should replace ``current`` for the same domain."""
    return _severity(candidate) > _severity(current)
