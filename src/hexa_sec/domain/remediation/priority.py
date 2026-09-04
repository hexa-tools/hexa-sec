"""Priority — the fix priority (context: remediation, SEC-24)."""

from __future__ import annotations

from enum import Enum


class Priority(Enum):
    """How urgent the remediation effort is."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

    @property
    def rank(self) -> int:
        return {Priority.LOW: 0, Priority.MEDIUM: 1, Priority.HIGH: 2}[self]

    @classmethod
    def normalize(cls, raw: str) -> Priority:
        """Map a raw label to a ``Priority``; unknown values are rejected."""
        cleaned = raw.strip().lower()
        try:
            return cls(cleaned)
        except ValueError as error:
            raise ValueError(f"unknown priority: {raw}") from error
