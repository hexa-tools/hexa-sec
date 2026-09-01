"""Snapshot — a scan at a date (context: temporal, SEC-22).

The state of a scan at one point in time. Both fields are required and
normalized, so the snapshot is never mis-matched in a delta (a padded scan_id or
date would silently break the comparison).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Snapshot:
    """The state of a scan at one point in time."""

    scan_id: str
    taken_on: str

    def __post_init__(self) -> None:
        if not self.scan_id or not self.scan_id.strip():
            raise ValueError("snapshot scan id cannot be empty")
        if not self.taken_on or not self.taken_on.strip():
            raise ValueError("snapshot taken_on cannot be empty")
        object.__setattr__(self, "scan_id", self.scan_id.strip())
        object.__setattr__(self, "taken_on", self.taken_on.strip())
