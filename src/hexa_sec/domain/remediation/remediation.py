"""Remediation — the recommended fix (context: remediation)."""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.remediation.remediation_status import RemediationStatus


@dataclass(frozen=True)
class Remediation:
    """A fix recommendation and its status."""

    finding_id: str
    instruction: str
    status: RemediationStatus = RemediationStatus.OPEN

    def __post_init__(self) -> None:
        if not self.instruction:
            raise ValueError("remediation instruction cannot be empty")
