"""AuditLogId + AuditLog — the append-only audit trail (context: evidence)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from hexa_sec.domain.consent.mandate import MandateId


@dataclass(frozen=True)
class AuditLogId:
    """An absolute identifier for an audit trail entry."""

    value: str


@dataclass(frozen=True)
class AuditLog:
    """A single immutable operation record, including the executed image digest."""

    entry_id: AuditLogId
    recorded_at: datetime
    action: str
    actor: str
    mandate_id: MandateId | None
    tenant_id: str | None = None
    scan_id: str | None = None
    image: str | None = None
    digest: str | None = None
    duration_ms: int | None = None

    def __post_init__(self) -> None:
        if not self.action or not self.action.strip():
            raise ValueError("audit action cannot be empty")
        if not self.actor or not self.actor.strip():
            raise ValueError("audit actor cannot be empty")
