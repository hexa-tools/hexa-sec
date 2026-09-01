"""AiSummary — the SLM-written report opening (context: ai_assist)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AiSummary:
    """The human-readable opening paragraph, written by the local SLM.

    The SLM explains — it never decides the score.
    """

    text: str

    def __post_init__(self) -> None:
        if not self.text:
            raise ValueError("ai summary text cannot be empty")
