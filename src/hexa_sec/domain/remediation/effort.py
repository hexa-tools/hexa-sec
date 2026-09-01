"""Effort — the estimated effort of a fix (context: remediation, SEC-24).

A non-negative number of minutes, rendered human-readably (``2h30``).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Effort:
    """The estimated effort, in minutes."""

    minutes: int

    def __post_init__(self) -> None:
        if self.minutes < 0:
            raise ValueError("effort minutes cannot be negative")

    def readable(self) -> str:
        """A compact human-readable duration (e.g. ``2h30``, ``45 min``)."""
        hours, minutes = divmod(self.minutes, 60)
        if hours and minutes:
            return f"{hours}h{minutes:02d}"
        if hours:
            return f"{hours}h"
        return f"{minutes} min"
