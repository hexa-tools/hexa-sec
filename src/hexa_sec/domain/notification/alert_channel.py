"""AlertChannel — where an alert is delivered (context: notification, SEC-25)."""

from __future__ import annotations

from enum import Enum


class AlertChannel(Enum):
    """The delivery channel of an alert."""

    SLACK = "slack"
    EMAIL = "email"
    WEBHOOK = "webhook"

    @classmethod
    def normalize(cls, raw: str) -> AlertChannel:
        """Map a raw label to an ``AlertChannel``; unknown values are rejected."""
        cleaned = raw.strip().lower().replace(" ", "_").replace("-", "_")
        try:
            return cls(cleaned)
        except ValueError as error:
            raise ValueError(f"unknown alert channel: {raw}") from error
