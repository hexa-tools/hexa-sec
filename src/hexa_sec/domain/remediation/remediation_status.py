"""RemediationStatus — lifecycle of a fix (context: remediation)."""

from __future__ import annotations

from enum import Enum


class RemediationStatus(Enum):
    """Lifecycle of a remediation effort."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    FIXED = "fixed"
    ACCEPTED = "accepted"

    def is_resolved(self) -> bool:
        return self is RemediationStatus.FIXED or self is RemediationStatus.ACCEPTED
