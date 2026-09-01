"""ApiRisk — the consolidated API-exposure inventory (context: api_risk).

``of`` deduplicates findings by (endpoint, category) keeping the highest severity
and sorts deterministically. Nothing raises when no API is exposed.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.api_risk.api_finding import ApiFinding


@dataclass(frozen=True)
class ApiRisk:
    """The API findings of the audited endpoints."""

    findings: tuple[ApiFinding, ...]

    @property
    def unauthenticated_count(self) -> int:
        """Number of findings on endpoints without authentication."""
        return sum(1 for finding in self.findings if not finding.endpoint.requires_auth())

    def unauthenticated_endpoints(self) -> tuple[str, ...]:
        """The ``METHOD path`` of unauthenticated endpoints, sorted."""
        return tuple(
            sorted(
                f"{finding.endpoint.method} {finding.endpoint.path}"
                for finding in self.findings
                if not finding.endpoint.requires_auth()
            )
        )

    @classmethod
    def of(cls, findings: Iterable[ApiFinding]) -> ApiRisk:
        """Build the inventory, deduplicated by (endpoint, category)."""
        seen: dict[tuple[str, str, str], ApiFinding] = {}
        for finding in findings:
            endpoint = finding.endpoint
            key = (endpoint.method, endpoint.path, finding.category.value)
            existing = seen.get(key)
            if existing is None or finding.severity.rank > existing.severity.rank:
                seen[key] = finding
        return cls(
            tuple(
                sorted(
                    seen.values(),
                    key=lambda f: (f.endpoint.method, f.endpoint.path, f.category.value),
                )
            )
        )
