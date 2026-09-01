"""Tests for the ApiRisk aggregate (context: api_risk)."""

from __future__ import annotations

from hexa_sec.domain.api_risk.api_endpoint import ApiEndpoint
from hexa_sec.domain.api_risk.api_finding import ApiFinding
from hexa_sec.domain.api_risk.api_risk import ApiRisk
from hexa_sec.domain.api_risk.owasp_category import OwaspApiCategory
from hexa_sec.domain.finding.severity import Severity


def _unauth_finding(
    path: str, category: OwaspApiCategory = OwaspApiCategory.BROKEN_AUTHENTICATION
) -> ApiFinding:
    return ApiFinding(
        endpoint=ApiEndpoint(method="GET", path=path, auth_required=False),
        category=category,
        severity=Severity.CRITICAL,
    )


def _auth_finding(
    path: str, category: OwaspApiCategory = OwaspApiCategory.BROKEN_AUTHENTICATION
) -> ApiFinding:
    return ApiFinding(
        endpoint=ApiEndpoint(method="GET", path=path, auth_required=True),
        category=category,
        severity=Severity.CRITICAL,
    )


def test_of_consolidates_findings() -> None:
    findings = (
        _unauth_finding("/v1/payments"),
        _auth_finding("/v1/orders"),
    )
    risk = ApiRisk.of(findings)
    assert len(risk.findings) == 2
    assert risk.unauthenticated_count == 1


def test_of_deduplicates_same_endpoint_category() -> None:
    findings = (_unauth_finding("/v1/payments"), _unauth_finding("/v1/payments"))
    risk = ApiRisk.of(findings)
    assert len(risk.findings) == 1


def test_of_keeps_higher_severity() -> None:
    low = ApiFinding(
        endpoint=ApiEndpoint(method="GET", path="/v1/payments", auth_required=True),
        category=OwaspApiCategory.BROKEN_AUTHENTICATION,
        severity=Severity.LOW,
    )
    high = ApiFinding(
        endpoint=ApiEndpoint(method="GET", path="/v1/payments", auth_required=True),
        category=OwaspApiCategory.BROKEN_AUTHENTICATION,
        severity=Severity.CRITICAL,
    )
    risk = ApiRisk.of((low, high))
    assert len(risk.findings) == 1
    assert risk.findings[0].severity is Severity.CRITICAL


def test_of_unauthenticated_endpoints() -> None:
    findings = (
        _unauth_finding("/v1/payments"),
        _auth_finding("/v1/orders"),
    )
    risk = ApiRisk.of(findings)
    assert risk.unauthenticated_endpoints() == ("GET /v1/payments",)
    assert risk.unauthenticated_count == 1


def test_of_empty_is_empty() -> None:
    risk = ApiRisk.of(())
    assert risk.findings == ()
    assert risk.unauthenticated_count == 0
    assert risk.unauthenticated_endpoints() == ()


def test_of_is_deterministic() -> None:
    findings = (
        _unauth_finding("/v1/payments"),
        _auth_finding("/v1/orders"),
    )
    first = ApiRisk.of(findings)
    second = ApiRisk.of(findings)
    assert first == second
    assert first.unauthenticated_count == second.unauthenticated_count


def test_of_order_independent() -> None:
    a = _unauth_finding("/v1/payments")
    b = _auth_finding("/v1/orders")
    first = ApiRisk.of((a, b))
    second = ApiRisk.of((b, a))
    assert first == second
    assert [f.endpoint.path for f in first.findings] == [f.endpoint.path for f in second.findings]
