"""RiskScore — the fix-first severity score (context: scoring)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskScore:
    """A 0..100 score combining severity, exploitability, exposure, impact."""

    value: float
    label: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 100.0:
            raise ValueError("risk score must be between 0 and 100")
