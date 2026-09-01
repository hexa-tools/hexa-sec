"""Tests for Tenant (context: tenant)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.tenant.tenant import Tenant, TenantId


def test_tenant_creation() -> None:
    tenant = Tenant(tenant_id=TenantId("tnt_0001"), name="Acme")
    assert tenant.name == "Acme"


def test_tenant_rejects_empty_name() -> None:
    with pytest.raises(ValueError):
        Tenant(tenant_id=TenantId("tnt_0002"), name="")
