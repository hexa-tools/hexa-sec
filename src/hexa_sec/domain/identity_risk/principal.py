"""Principal — an identity (context: identity_risk, SEC-19).

An identity (user / group / service account). The value is normalized (stripped)
so the identifier is never mis-matched in aggregation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Principal:
    """A user, group or technical account identity."""

    value: str

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("principal cannot be empty")
        object.__setattr__(self, "value", self.value.strip())
