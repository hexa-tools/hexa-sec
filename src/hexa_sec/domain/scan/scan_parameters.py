"""ScanParameters — depth, exclusions and window (context: scan)."""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.scan.scan_depth import ScanDepth
from hexa_sec.domain.scan.scan_window import ScanWindow


@dataclass(frozen=True)
class ScanParameters:
    """How a scan is run: how deep, and what to avoid."""

    depth: ScanDepth
    exclusions: tuple[str, ...] = ()
    window: ScanWindow | None = None

    def __post_init__(self) -> None:
        for exclusion in self.exclusions:
            if not exclusion.strip():
                raise ValueError("scan exclusion cannot be empty")
