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
