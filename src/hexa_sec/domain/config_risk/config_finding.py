"""ConfigFinding — a CIS benchmark deviation (context: config_risk)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConfigFinding:
    """A configuration deviation against a benchmark."""

    benchmark: str
    check: str

    def __post_init__(self) -> None:
        if not self.benchmark:
            raise ValueError("config finding benchmark cannot be empty")
        if not self.check:
            raise ValueError("config finding check cannot be empty")
