"""Bound context 28 — Tenant (per-client isolation)."""

from __future__ import annotations

from hexa_sec.domain.tenant.tenant import Tenant, TenantId
from hexa_sec.domain.tenant.tenants import Tenants

__all__ = ["Tenant", "TenantId", "Tenants"]
