"""MobileRisk — the consolidated mobile-findings inventory (context: mobile_risk).

``of`` deduplicates findings by (package, issue) keeping the secret-embedding
posture and sorts deterministically. Nothing raises when no app embeds a secret.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.mobile_risk.mobile_finding import MobileFinding


@dataclass(frozen=True)
class MobileRisk:
    """The mobile findings of the audited applications."""

    findings: tuple[MobileFinding, ...]

    @property
    def secret_count(self) -> int:
        """Number of findings embedding a secret."""
        return sum(1 for finding in self.findings if finding.embeds_secret())

    def secret_packages(self) -> tuple[str, ...]:
        """The packages embedding a secret, sorted."""
        return tuple(
            sorted(finding.package for finding in self.findings if finding.embeds_secret())
        )

    @classmethod
    def of(cls, findings: Iterable[MobileFinding]) -> MobileRisk:
        """Build the inventory, deduplicated by (package, issue)."""
        seen: dict[tuple[str, str], MobileFinding] = {}
        for finding in findings:
            key = (finding.package, finding.issue)
            existing = seen.get(key)
            if existing is None or _prefer(finding, existing):
                seen[key] = finding
        return cls(tuple(sorted(seen.values(), key=lambda f: (f.package, f.issue))))


def _prefer(candidate: MobileFinding, current: MobileFinding) -> bool:
    """Whether ``candidate`` should replace ``current`` for the same key.

    A secret-embedding finding wins, then a deterministic tie-break on the
    secret type — total order, independent of arrival order.
    """
    candidate_key = (
        int(candidate.embeds_secret()),
        candidate.secret_type.value if candidate.secret_type else "",
    )
    current_key = (
        int(current.embeds_secret()),
        current.secret_type.value if current.secret_type else "",
    )
    return candidate_key > current_key
