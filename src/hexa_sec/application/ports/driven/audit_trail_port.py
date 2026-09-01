"""AuditTrailPort — the auditable execution record boundary (driven port)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class AuditRecord(TypedDict):
    """A traceable execution record: scan -> image@digest -> mandate -> duration."""

    tenant_id: str
    entry_id: str
    scan_id: str
    mandate_id: str
    action: str
    actor: str
    image: str
    digest: str
    duration_ms: int
    recorded_at: str


class AuditTrailPort(ABC):
    """Persist execution metadata; every access is tenant-scoped."""

    @abstractmethod
    def save_audit(self, record: AuditRecord) -> None:
        raise NotImplementedError  # pragma: no cover

    @abstractmethod
    def load_audit(self, tenant_id: str) -> list[AuditRecord]:
        raise NotImplementedError  # pragma: no cover
