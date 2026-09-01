"""ApiFinding — an API security exposure (context: api_risk)."""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.api_risk.api_endpoint import ApiEndpoint
from hexa_sec.domain.api_risk.owasp_category import OwaspApiCategory
from hexa_sec.domain.finding.severity import Severity


@dataclass(frozen=True)
class ApiFinding:
    """An OWASP API vulnerability on an endpoint."""

    endpoint: ApiEndpoint
    category: OwaspApiCategory
    severity: Severity = Severity.MEDIUM

    def __post_init__(self) -> None:
        if not isinstance(self.endpoint, ApiEndpoint):
            raise ValueError("api finding endpoint must be an ApiEndpoint")
        if not isinstance(self.category, OwaspApiCategory):
            raise ValueError("api finding category must be an OwaspApiCategory")
        if not isinstance(self.severity, Severity):
            raise ValueError("api finding severity must be a Severity")
        if not self.endpoint.requires_auth() and self.severity.rank < Severity.HIGH.rank:
            object.__setattr__(self, "severity", Severity.HIGH)
