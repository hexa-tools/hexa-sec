"""ScanWindow — the scheduled time slot of a scan (context: scan)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScanWindow:
    """A daily window (inclusive start, exclusive end hour) for a scan."""

    start_hour: int
    end_hour: int

    def __post_init__(self) -> None:
        if not 0 <= self.start_hour <= 23:
            raise ValueError("start hour must be between 0 and 23")
        if not 0 <= self.end_hour <= 23:
            raise ValueError("end hour must be between 0 and 23")
        if self.start_hour == self.end_hour:
            raise ValueError("scan window cannot be empty")

    def duration(self) -> int:
        return (self.end_hour - self.start_hour) % 24

    def is_night(self) -> bool:
        return self.start_hour >= 22 or self.end_hour <= 6
