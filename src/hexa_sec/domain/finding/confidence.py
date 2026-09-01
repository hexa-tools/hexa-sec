"""Confidence — how sure we are of a finding (context: finding)."""

from __future__ import annotations

from enum import Enum


class Confidence(Enum):
    """Certainty scale for a normalized finding."""

    CERTAIN = "certain"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    GUESS = "guess"

    @property
    def rank(self) -> int:
        return {
            Confidence.CERTAIN: 4,
            Confidence.HIGH: 3,
            Confidence.MEDIUM: 2,
            Confidence.LOW: 1,
            Confidence.GUESS: 0,
        }[self]
