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
        """Whether the fix is done (FIXED) or the risk is tolerated (ACCEPTED)."""
        return self is RemediationStatus.FIXED or self is RemediationStatus.ACCEPTED

    def can_transition_to(self, other: RemediationStatus) -> bool:
        """Whether a status change ``self -> other`` is a valid lifecycle step.

        OPEN may go to IN_PROGRESS or ACCEPTED; IN_PROGRESS may go to FIXED or
        ACCEPTED. Terminal states (FIXED/ACCEPTED) and the same status never
        transition.
        """
        return other in _ALLOWED[self]


_ALLOWED = {
    RemediationStatus.OPEN: {RemediationStatus.IN_PROGRESS, RemediationStatus.ACCEPTED},
    RemediationStatus.IN_PROGRESS: {RemediationStatus.FIXED, RemediationStatus.ACCEPTED},
    RemediationStatus.FIXED: set(),
    RemediationStatus.ACCEPTED: set(),
}
