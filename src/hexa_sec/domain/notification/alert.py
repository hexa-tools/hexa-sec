"""Alert — a notification trigger (context: notification)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Alert:
    """An alert to deliver on a channel."""

    subject: str
    channel: str

    def __post_init__(self) -> None:
        if not self.subject:
            raise ValueError("alert subject cannot be empty")
        if not self.channel:
            raise ValueError("alert channel cannot be empty")
