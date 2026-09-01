"""Tests for the Tenants aggregate (context: tenant)."""

from __future__ import annotations

from hexa_sec.domain.tenant.tenant import Tenant, TenantId
from hexa_sec.domain.tenant.tenants import Tenants


def _tenant(tenant_id: str, name: str = "Acme") -> Tenant:
    return Tenant(tenant_id=TenantId(tenant_id), name=name)


def test_of_deduplicates_by_tenant_id() -> None:
    tenants = (_tenant("tnt_0001"), _tenant("tnt_0001"))
    registry = Tenants.of(tenants)
    assert len(registry.tenants) == 1


def test_of_keeps_same_name_distinct_ids() -> None:
    tenants = (_tenant("tnt_0001", name="Acme"), _tenant("tnt_0002", name="Acme"))
    registry = Tenants.of(tenants)
    assert len(registry.tenants) == 2


def test_of_finds_tenant() -> None:
    registry = Tenants.of((_tenant("tnt_0001"), _tenant("tnt_0002", name="Beta")))
    assert registry.find(TenantId("tnt_0002")).name == "Beta"


def test_of_find_missing_returns_none() -> None:
    registry = Tenants.of((_tenant("tnt_0001"),))
    assert registry.find(TenantId("tnt_0999")) is None


def test_of_empty_is_empty() -> None:
    registry = Tenants.of(())
    assert registry.tenants == ()
    assert registry.find(TenantId("tnt_0001")) is None


def test_of_is_deterministic() -> None:
    tenants = (_tenant("tnt_0001"), _tenant("tnt_0002", name="Beta"))
    first = Tenants.of(tenants)
    second = Tenants.of(tenants)
    assert first == second


# --- Category: stabilité / déterminisme (nom du tenant, ordre-indépendant) ---
def test_of_dedup_is_order_independent_for_name() -> None:
    acme = _tenant("tnt_0001", name="Acme")
    acme_corp = _tenant("tnt_0001", name="Acme Corp")
    first = Tenants.of((acme, acme_corp))
    second = Tenants.of((acme_corp, acme))
    assert first == second
    assert first.tenants[0].name == "Acme Corp"
