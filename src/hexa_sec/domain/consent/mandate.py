"""MandateLevel + MandateId + Mandate — the legal authorization to scan.

Bound context 6 (consent). This is the **non-negotiable** Godfrain gate: no
scan is ever launched without a valid mandate that covers the exact target and
is within its validity period.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class MandateLevel(Enum):
    """The authorization level granted by the client."""

    STANDARD = "standard"
    OFFENSIVE = "offensive"


@dataclass(frozen=True)
class MandateId:
    """An absolute identifier for a mandate."""

    value: str


@dataclass(frozen=True)
class Mandate:
    """The versioned legal agreement authorizing a scan."""

    mandate_id: MandateId
    client: str
    targets: tuple[str, ...]
    start_date: date
    end_date: date
    level: MandateLevel
    signature: str

    def __post_init__(self) -> None:
        if not self.targets:
            raise ValueError("mandate must cover at least one target")
        if self.end_date < self.start_date:
            raise ValueError("mandate end date cannot precede start date")
        if not self.signature or not self.signature.strip():
            raise ValueError("mandate must be signed")
        if not self.client or not self.client.strip():
            raise ValueError("mandate client cannot be empty")

    def covers(self, target: str) -> bool:
        return target in self.targets

    def is_valid(self, as_of: date | None = None) -> bool:
        today = as_of or date.today()
        return self.start_date <= today <= self.end_date

    def is_offensive(self) -> bool:
        return self.level is MandateLevel.OFFENSIVE
