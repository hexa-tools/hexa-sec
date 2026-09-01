"""ScoreLevel — the interpreted risk level (context: scoring)."""

from __future__ import annotations

from enum import Enum


class ScoreLevel(Enum):
    """The fix-first risk level, derived deterministically from a 0..100 score."""

    CRITICAL = "critical"
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"

    @classmethod
    def for_value(cls, value: float) -> ScoreLevel:
        if value >= 80:
            return cls.CRITICAL
        if value >= 60:
            return cls.HIGH
        if value >= 40:
            return cls.MODERATE
        return cls.LOW
