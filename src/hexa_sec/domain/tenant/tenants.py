"""Tenants — the strict isolation registry (context: tenant).

``of`` deduplicates tenants by ``TenantId`` and ``find`` is fail-closed: an
unknown tenant returns ``None``, never a default or another client's data.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.tenant.tenant import Tenant, TenantId


@dataclass(frozen=True)
class Tenants:
    """The registry of known tenants, keyed by :class:`TenantId`."""

    tenants: tuple[Tenant, ...]

    def find(self, tenant_id: TenantId) -> Tenant | None:
        """Return the tenant with the given id, or ``None`` (fail-closed)."""
        for tenant in self.tenants:
            if tenant.tenant_id == tenant_id:
                return tenant
        return None

    @classmethod
    def of(cls, tenants: Iterable[Tenant]) -> Tenants:
        """Build the registry, deduplicated by ``TenantId`` and sorted."""
        seen: dict[str, Tenant] = {}
        for tenant in tenants:
            key = tenant.tenant_id.value
            existing = seen.get(key)
            if existing is None or tenant.name > existing.name:
                seen[key] = tenant
        return cls(tuple(sorted(seen.values(), key=lambda t: t.tenant_id.value)))
