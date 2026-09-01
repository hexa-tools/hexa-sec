"""Threat — a known actor or campaign (context: threat_intel)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Threat:
    """A known threat actor or campaign."""

    actor: str
    tactic: str

    def __post_init__(self) -> None:
        if not self.actor:
            raise ValueError("threat actor cannot be empty")
        if not self.tactic:
            raise ValueError("threat tactic cannot be empty")
