"""RiskScore — the fix-first severity score (context: scoring)."""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.scoring.score_level import ScoreLevel


@dataclass(frozen=True)
class RiskScore:
    """A 0..100 score combining severity, exploitability, exposure, impact.

    ``label`` is the human-readable level; use :meth:`from_value` to build it
    coherently with the value.
    """

    value: float
    label: str

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 100.0:
            raise ValueError("risk score must be between 0 and 100")
        if not self.label or not self.label.strip():
            raise ValueError("risk score label cannot be empty")

    @property
    def level(self) -> ScoreLevel:
        return ScoreLevel.for_value(self.value)

    @classmethod
    def from_value(cls, value: float) -> RiskScore:
        return cls(value=value, label=ScoreLevel.for_value(value).value)

    def is_coherent(self) -> bool:
        """True when ``label`` reflects the level derived from ``value``.

        Lets the scoring checker flag a label that contradicts the value
        (e.g. value=95 with label="low") instead of silently trusting it.
        """
        return self.label.strip().lower() == self.level.value
