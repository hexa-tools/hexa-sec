"""CloudRisk — the consolidated cloud-exposure inventory (context: cloud_risk).

``of`` deduplicates findings by resource (keeping the exposed one) and sorts
deterministically. Nothing raises when no resource is exposed or none is present.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.cloud_risk.cloud_finding import CloudFinding


@dataclass(frozen=True)
class CloudRisk:
    """The cloud findings of the audited resources."""

    findings: tuple[CloudFinding, ...]

    @property
    def exposed_count(self) -> int:
        """Number of exposed (public) resources."""
        return sum(1 for finding in self.findings if finding.exposed())

    def exposed_resources(self) -> tuple[str, ...]:
        """The exposed resource ids, sorted."""
        return tuple(
            sorted(finding.resource.resource_id for finding in self.findings if finding.exposed())
        )

    @classmethod
    def of(cls, findings: Iterable[CloudFinding]) -> CloudRisk:
        """Build the inventory, deduplicated by resource (exposed kept)."""
        seen: dict[str, CloudFinding] = {}
        for finding in findings:
            existing = seen.get(finding.resource.resource_id)
            if existing is None or _prefer(finding, existing):
                seen[finding.resource.resource_id] = finding
        return cls(tuple(sorted(seen.values(), key=lambda f: f.resource.resource_id)))


def _prefer(candidate: CloudFinding, current: CloudFinding) -> bool:
    """Whether ``candidate`` should replace ``current`` for the same resource.

    Total order (exposed first, then severity) so the consolidation is
    independent of arrival order.
    """
    candidate_key = (int(candidate.exposed()), candidate.severity.rank)
    current_key = (int(current.exposed()), current.severity.rank)
    return candidate_key > current_key
