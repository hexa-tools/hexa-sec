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
    """A single immutable operation record."""

    entry_id: AuditLogId
    recorded_at: datetime
    action: str
    actor: str
    mandate_id: MandateId | None

    def __post_init__(self) -> None:
        if not self.action:
            raise ValueError("audit action cannot be empty")
        if not self.actor:
            raise ValueError("audit actor cannot be empty")
