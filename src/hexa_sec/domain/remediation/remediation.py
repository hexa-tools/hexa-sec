"""Remediation — the recommended fix and its lifecycle (context: remediation, SEC-24).

A fix always points to a real finding (non-empty id), carries its estimated
effort and priority, and its status. It is immutable: a status change produces a
new :class:`Remediation` through :meth:`transition_to`, which refuses illegal
steps (a terminal status can never be entered directly).
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.remediation.effort import Effort
from hexa_sec.domain.remediation.priority import Priority
from hexa_sec.domain.remediation.remediation_status import RemediationStatus


@dataclass(frozen=True)
class Remediation:
    """A fix recommendation and its lifecycle state."""

    finding_id: str
    instruction: str
    status: RemediationStatus = RemediationStatus.OPEN
    effort: Effort | None = None
    priority: Priority | None = None

    def transition_to(self, new_status: RemediationStatus) -> Remediation:
        """Return a new :class:`Remediation` with a validated status change.

        Raises ``ValueError`` for an illegal step (e.g. OPEN -> FIXED, or from a
        terminal status) — a remediation never jumps to a terminal state directly.
        """
        if not isinstance(new_status, RemediationStatus):
            raise ValueError("remediation status must be a RemediationStatus")
        if not self.status.can_transition_to(new_status):
            raise ValueError(
                f"illegal remediation transition: {self.status.value} -> {new_status.value}"
            )
        instance = Remediation(
            finding_id=self.finding_id,
            instruction=self.instruction,
            status=RemediationStatus.OPEN,
            effort=self.effort,
            priority=self.priority,
        )
        object.__setattr__(instance, "status", new_status)
        return instance

    def __post_init__(self) -> None:
        if not self.finding_id or not self.finding_id.strip():
            raise ValueError("remediation finding_id cannot be empty")
        if not self.instruction or not self.instruction.strip():
            raise ValueError("remediation instruction cannot be empty")
        if not isinstance(self.status, RemediationStatus):
            raise ValueError("remediation status must be a RemediationStatus")
        if self.status is RemediationStatus.FIXED or self.status is RemediationStatus.ACCEPTED:
            raise ValueError(
                "remediation cannot be created in a terminal status (use transition_to)"
            )
        if self.effort is not None and not isinstance(self.effort, Effort):
            raise ValueError("remediation effort must be an Effort")
        if self.priority is not None and not isinstance(self.priority, Priority):
            raise ValueError("remediation priority must be a Priority")
        object.__setattr__(self, "finding_id", self.finding_id.strip())
        object.__setattr__(self, "instruction", self.instruction.strip())
