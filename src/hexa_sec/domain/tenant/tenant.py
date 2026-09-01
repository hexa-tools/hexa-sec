"""TenantId + Tenant — strict per-client isolation (context: tenant)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TenantId:
    """An absolute identifier for a tenant."""

    value: str


@dataclass(frozen=True)
class Tenant:
    """A client isolation boundary. No tenant sees another's data."""

    tenant_id: TenantId
    name: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("tenant name cannot be empty")
