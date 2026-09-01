"""ScoreComponents — the normalized inputs of the scoring engine (context: scoring).

Every component is optional: a missing value is simply not used, never invented.
Severity is the usual anchor, but a finding without any of them yields no score.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.finding.severity import Severity

RANGES = ("exploitability", "exposure", "impact", "facility")


@dataclass(frozen=True)
class ScoreComponents:
    """The components that feed the deterministic score."""

    severity: Severity | None = None
    exploitability: float | None = None
    exposure: float | None = None
    impact: float | None = None
    facility: float | None = None

    def __post_init__(self) -> None:
        for name in RANGES:
            value = getattr(self, name)
            if value is not None and not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
