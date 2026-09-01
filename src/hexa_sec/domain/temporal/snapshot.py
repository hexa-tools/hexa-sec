"""Snapshot — a scan at a date (context: temporal)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Snapshot:
    """The state of a scan at one point in time."""

    scan_id: str
    taken_on: str

    def __post_init__(self) -> None:
        if not self.scan_id:
            raise ValueError("snapshot scan id cannot be empty")
