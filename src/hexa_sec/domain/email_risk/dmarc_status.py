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

    @classmethod
    def normalize(cls, raw: str) -> DmarcStatus:
        """Map a raw DMARC value to a ``DmarcStatus``; unknown values are rejected.

        Accepts the canonical labels (none / reject / quarantine / missing) and
        the DMARC record ``p=`` policy (e.g. ``p=none``, ``v=DMARC1; p=reject``).
        Never guesses an unknown posture.
        """
        cleaned = raw.strip().lower()
        if "=" in cleaned:
            for part in cleaned.split(";"):
                part = part.strip()
                if part.startswith("p="):
                    cleaned = part[2:].strip()
                    break
        cleaned = cleaned.replace(" ", "_").replace("-", "_")
        try:
            return cls(cleaned)
        except ValueError as error:
            raise ValueError(f"unknown dmarc status: {raw}") from error
