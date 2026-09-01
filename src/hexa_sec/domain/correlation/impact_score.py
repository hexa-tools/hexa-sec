"""ImpactScore — the combined impact level of a correlation (context: correlation)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ImpactLevel(Enum):
    """Narrowed impact ladder used when reporting a correlation."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class ImpactScore:
    """A 0..1 combined impact score for a correlation."""

    value: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            raise ValueError("impact score must be between 0 and 1")

    def level(self) -> ImpactLevel:
        if self.value >= 0.8:
            return ImpactLevel.CRITICAL
        if self.value >= 0.6:
            return ImpactLevel.HIGH
        if self.value >= 0.3:
            return ImpactLevel.MEDIUM
        return ImpactLevel.LOW
