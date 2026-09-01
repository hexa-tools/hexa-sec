"""TenantId + Tenant — strict per-client isolation (context: tenant).

A ``TenantId`` is the absolute scope of every scan, secret and report. Both
value objects are normalized and validated so no isolation boundary is ever
ambiguous.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TenantId:
    """An absolute identifier for a tenant."""

    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise ValueError("tenant id cannot be empty")
        object.__setattr__(self, "value", self.value.strip())


@dataclass(frozen=True)
class Tenant:
    """A client isolation boundary. No tenant sees another's data."""

    tenant_id: TenantId
    name: str

    def __post_init__(self) -> None:
        if not isinstance(self.tenant_id, TenantId):
            raise ValueError("tenant tenant_id must be a TenantId")
        if not self.name.strip():
            raise ValueError("tenant name cannot be empty")
        object.__setattr__(self, "name", self.name.strip())
