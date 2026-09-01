"""AlertType — the trigger of an alert (context: notification, SEC-25)."""

from __future__ import annotations

from enum import Enum


class AlertType(Enum):
    """What triggered the alert."""

    NEWSECRET = "new_secret"
    CRITICALCVE = "critical_cve"
    NEWEXPOSURE = "new_exposure"
    COMPLIANCEGAP = "compliance_gap"
    FIX_RESOLVED = "fix_resolved"

    @classmethod
    def normalize(cls, raw: str) -> AlertType:
        """Map a raw label to an ``AlertType``; unknown values are rejected.

        Accepts space/hyphen/underscore variations and the compact member name
        (e.g. ``NEWSECRET``) — never guesses an unknown trigger.
        """
        cleaned = raw.strip().lower().replace(" ", "_").replace("-", "_")
        try:
            return cls(cleaned)
        except ValueError:
            compact = cleaned.replace("_", "")
            for member in cls:
                if member.value.replace("_", "") == compact:
                    return member
            raise ValueError(f"unknown alert type: {raw}") from None
