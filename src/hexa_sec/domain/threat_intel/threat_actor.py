"""ThreatActor — a known threat actor (context: threat_intel, SEC-20).

An actor (APT-41, FIN7...) with a short description. Both fields are normalized
so the identifier is never mis-matched in aggregation.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ThreatActor:
    """A known threat actor or campaign sponsor."""

    identifier: str
    description: str

    def __post_init__(self) -> None:
        if not self.identifier or not self.identifier.strip():
            raise ValueError("threat actor identifier cannot be empty")
        if not self.description or not self.description.strip():
            raise ValueError("threat actor description cannot be empty")
        object.__setattr__(self, "identifier", self.identifier.strip())
        object.__setattr__(self, "description", self.description.strip())
