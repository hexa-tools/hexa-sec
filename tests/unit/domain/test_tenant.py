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


def test_tenant_id_rejects_empty() -> None:
    with pytest.raises(ValueError):
        TenantId("")


def test_tenant_id_rejects_blank() -> None:
    with pytest.raises(ValueError):
        TenantId("   ")


def test_tenant_id_normalizes_value() -> None:
    assert TenantId("  tnt_0001  ").value == "tnt_0001"


def test_tenant_rejects_non_tenant_id() -> None:
    with pytest.raises(ValueError):
        Tenant(tenant_id="tnt_0001", name="Acme")  # type: ignore[arg-type]


def test_tenant_normalizes_name() -> None:
    assert Tenant(tenant_id=TenantId("tnt_0001"), name="  Acme  ").name == "Acme"
