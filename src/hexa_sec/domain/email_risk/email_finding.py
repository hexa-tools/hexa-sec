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

    def __post_init__(self) -> None:
        if not isinstance(self.record, EmailRecord):
            raise ValueError("email finding record must be an EmailRecord")
        if not isinstance(self.dmarc, DmarcStatus):
            raise ValueError("email finding dmarc must be a DmarcStatus")
