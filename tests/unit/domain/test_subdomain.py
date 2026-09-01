"""Tests for Subdomain (context: dns_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.dns_risk.subdomain import Subdomain


def test_subdomain_creation() -> None:
    subdomain = Subdomain(name="admin.acme.example", resolved=True)
    assert subdomain.resolved is True
    assert subdomain.wildcard is False


def test_subdomain_rejects_empty_name() -> None:
    with pytest.raises(ValueError):
        Subdomain(name="")
