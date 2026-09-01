"""ImpactLevel — the business criticality of an asset (context: business_impact, SEC-23).

Distinct from the correlation ``ImpactLevel`` (a 0..1 reported-ladder): this one
grades the business weight of an asset (NORMAL → CRITICAL). A CRITICAL asset has
the highest rank. Normalization never invents a level.
"""

from __future__ import annotations

from enum import Enum


class ImpactLevel(Enum):
    """The business criticality of an asset."""

    NORMAL = "normal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def rank(self) -> int:
        return {
            ImpactLevel.NORMAL: 0,
            ImpactLevel.LOW: 1,
            ImpactLevel.MEDIUM: 2,
            ImpactLevel.HIGH: 3,
            ImpactLevel.CRITICAL: 4,
        }[self]

    @property
    def is_critical(self) -> bool:
        """Whether the asset is business-critical (highest weight)."""
        return self is ImpactLevel.CRITICAL

    @classmethod
    def normalize(cls, raw: str) -> ImpactLevel:
        """Map a raw label to an ``ImpactLevel``; unknown values are rejected."""
        cleaned = raw.strip().lower().replace(" ", "_").replace("-", "_")
        try:
            return cls(cleaned)
        except ValueError as error:
            raise ValueError(f"unknown impact level: {raw}") from error
