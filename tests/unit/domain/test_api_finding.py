"""Tests for ApiFinding (context: api_risk)."""

from __future__ import annotations

import pytest

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
    endpoint = ApiEndpoint(method="GET", path="/v1/payments", auth_required=True)
    finding = ApiFinding(
        endpoint=endpoint, category=OwaspApiCategory.BROKEN_OBJECT_LEVEL_AUTHORIZATION
    )
    assert finding.severity is Severity.MEDIUM


def _unauth_endpoint() -> ApiEndpoint:
    return ApiEndpoint(method="GET", path="/v1/payments", auth_required=False)


def _auth_endpoint() -> ApiEndpoint:
    return ApiEndpoint(method="GET", path="/v1/payments", auth_required=True)


def test_api_finding_unauth_raises_severity_to_high() -> None:
    low = ApiFinding(
        endpoint=_unauth_endpoint(),
        category=OwaspApiCategory.BROKEN_AUTHENTICATION,
        severity=Severity.LOW,
    )
    medium = ApiFinding(
        endpoint=_unauth_endpoint(),
        category=OwaspApiCategory.BROKEN_AUTHENTICATION,
        severity=Severity.MEDIUM,
    )
    assert low.severity is Severity.HIGH
    assert medium.severity is Severity.HIGH


def test_api_finding_unauth_default_severity_raised() -> None:
    finding = ApiFinding(
        endpoint=_unauth_endpoint(), category=OwaspApiCategory.BROKEN_AUTHENTICATION
    )
    assert finding.severity is Severity.HIGH


def test_api_finding_unauth_keeps_high() -> None:
    finding = ApiFinding(
        endpoint=_unauth_endpoint(),
        category=OwaspApiCategory.BROKEN_AUTHENTICATION,
        severity=Severity.HIGH,
    )
    assert finding.severity is Severity.HIGH


def test_api_finding_auth_keeps_low() -> None:
    finding = ApiFinding(
        endpoint=_auth_endpoint(),
        category=OwaspApiCategory.BROKEN_AUTHENTICATION,
        severity=Severity.LOW,
    )
    assert finding.severity is Severity.LOW


def test_api_finding_rejects_non_endpoint() -> None:
    with pytest.raises(ValueError):
        ApiFinding(endpoint="/v1/payments", category=OwaspApiCategory.BROKEN_AUTHENTICATION)  # type: ignore[arg-type]


def test_api_finding_rejects_non_category() -> None:
    with pytest.raises(ValueError):
        ApiFinding(endpoint=_auth_endpoint(), category="api2")  # type: ignore[arg-type]


def test_api_finding_rejects_non_severity() -> None:
    with pytest.raises(ValueError):
        ApiFinding(
            endpoint=_auth_endpoint(),
            category=OwaspApiCategory.BROKEN_AUTHENTICATION,
            severity="high",
        )  # type: ignore[arg-type]
