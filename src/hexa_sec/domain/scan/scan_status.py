"""ScanStatus — the lifecycle state of a scan (context: scan)."""

from __future__ import annotations

from enum import Enum


class ScanStatus(Enum):
    """Lifecycle of a scan."""

    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"

    def is_terminal(self) -> bool:
        return self in (ScanStatus.DONE, ScanStatus.FAILED)
