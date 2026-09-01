"""ScanDepth — how deep a scan goes (context: scan)."""

from __future__ import annotations

from enum import Enum


class ScanDepth(Enum):
    """The audit depth of a scan."""

    QUICK = "quick"
    COMPLETE = "complete"
    OFFENSIVE = "offensive"

    def requires_offensive_mandate(self) -> bool:
        return self is ScanDepth.OFFENSIVE
