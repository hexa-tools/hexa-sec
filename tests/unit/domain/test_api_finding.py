"""Tests for ApiFinding (context: api_risk)."""

from __future__ import annotations

from hexa_sec.domain.api_risk.api_endpoint import ApiEndpoint
from hexa_sec.domain.api_risk.api_finding import ApiFinding
from hexa_sec.domain.api_risk.owasp_category import OwaspApiCategory
from hexa_sec.domain.finding.severity import Severity


def test_api_finding_creation() -> None:
    endpoint = ApiEndpoint(method="GET", path="/v1/payments")
    finding = ApiFinding(
        endpoint=endpoint,
        category=OwaspApiCategory.BROKEN_OBJECT_LEVEL_AUTHORIZATION,
        severity=Severity.HIGH,
    )
    assert finding.endpoint is endpoint
    assert finding.category is OwaspApiCategory.BROKEN_OBJECT_LEVEL_AUTHORIZATION
    assert finding.severity is Severity.HIGH


def test_api_finding_default_severity() -> None:
    endpoint = ApiEndpoint(method="GET", path="/v1/payments")
    finding = ApiFinding(
        endpoint=endpoint, category=OwaspApiCategory.BROKEN_OBJECT_LEVEL_AUTHORIZATION
    )
    assert finding.severity is Severity.MEDIUM
