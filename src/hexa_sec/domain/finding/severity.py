"""Severity — the impact level of a finding (context: finding)."""

from __future__ import annotations

from enum import Enum


class Severity(Enum):
    """Standard severity scale used across all normalized findings."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def rank(self) -> int:
        return {
            Severity.INFO: 0,
            Severity.LOW: 1,
            Severity.MEDIUM: 2,
            Severity.HIGH: 3,
            Severity.CRITICAL: 4,
        }[self]
