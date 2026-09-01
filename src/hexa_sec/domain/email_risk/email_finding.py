"""EmailFinding — an email spoofing exposure (context: email_risk)."""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.email_risk.dmarc_status import DmarcStatus
from hexa_sec.domain.email_risk.email_record import EmailRecord


@dataclass(frozen=True)
class EmailFinding:
    """A domain at risk of email spoofing."""

    record: EmailRecord
    dmarc: DmarcStatus

    @property
    def domain(self) -> str:
        return self.record.domain

    def spoofable(self) -> bool:
        return self.dmarc in (DmarcStatus.NONE, DmarcStatus.MISSING)
