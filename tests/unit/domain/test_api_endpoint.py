"""Tests for ApiEndpoint (context: api_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.api_risk.api_endpoint import ApiEndpoint


def test_api_endpoint_creation() -> None:
    endpoint = ApiEndpoint(method="get", path="/v1/payments")
    assert endpoint.method == "GET"
    assert endpoint.path == "/v1/payments"


def test_api_endpoint_auth_required() -> None:
    endpoint = ApiEndpoint(method="POST", path="/v1/payments", auth_required=True)
    assert endpoint.requires_auth() is True


def test_api_endpoint_rejects_empty_method() -> None:
    with pytest.raises(ValueError):
        ApiEndpoint(method="", path="/v1/payments")


def test_api_endpoint_rejects_unsupported_method() -> None:
    with pytest.raises(ValueError):
        ApiEndpoint(method="TRACE", path="/v1/payments")


def test_api_endpoint_rejects_empty_path() -> None:
    with pytest.raises(ValueError):
        ApiEndpoint(method="GET", path="")
