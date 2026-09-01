"""DmarcStatus — the DMARC policy posture (context: email_risk)."""

from __future__ import annotations

from enum import Enum


class DmarcStatus(Enum):
    """The DMARC policy found for a domain."""

    REJECT = "reject"
    QUARANTINE = "quarantine"
    NONE = "none"
    MISSING = "missing"

    @property
    def enforced(self) -> bool:
        return self in (DmarcStatus.REJECT, DmarcStatus.QUARANTINE)
