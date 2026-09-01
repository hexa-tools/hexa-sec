"""Alert — a notification trigger (context: notification, SEC-25).

An alert names the subject, its alert type, severity, delivery channel and the
finding that triggered it. A CRITICAL alert must point to a real finding — never
an empty/speculative alert. Non-critical alerts may omit the finding.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.notification.alert_channel import AlertChannel
from hexa_sec.domain.notification.alert_type import AlertType


@dataclass(frozen=True)
class Alert:
    """A single notification trigger."""

    subject: str
    alert_type: AlertType
    severity: Severity
    channel: AlertChannel
    finding_id: FindingId | None = None

    def __post_init__(self) -> None:
        if not self.subject or not self.subject.strip():
            raise ValueError("alert subject cannot be empty")
        if not isinstance(self.alert_type, AlertType):
            raise ValueError("alert alert_type must be an AlertType")
        if not isinstance(self.severity, Severity):
            raise ValueError("alert severity must be a Severity")
        if not isinstance(self.channel, AlertChannel):
            raise ValueError("alert channel must be an AlertChannel")
        if self.severity is Severity.CRITICAL and (
            self.finding_id is None or not self.finding_id.value.strip()
        ):
            raise ValueError("critical alert requires a source finding")
        object.__setattr__(self, "subject", self.subject.strip())
