"""AuditConsent — the append-only consent log (context: consent)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from hexa_sec.domain.consent.mandate import MandateId


@dataclass(frozen=True)
class AuditConsent:
    """A single recorded consent decision, forever traceable."""

    mandate_id: MandateId
    recorded_at: datetime
    actor: str
    decision: str

    def __post_init__(self) -> None:
        if not self.actor:
            raise ValueError("consent actor cannot be empty")
        if not self.decision:
            raise ValueError("consent decision cannot be empty")
