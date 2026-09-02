"""ScoreReportServicePort — scoring and ordering (US-3)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class ScoreItem(TypedDict):
    """A finding/correlation to score, with its deterministic components."""

    finding_id: str
    severity: str
    exploitability: float | None
    exposure: float | None
    impact: float | None
    facility: float | None


class ScoredItem(TypedDict):
    """A scored item: its 0..100 score and coherent label."""

    finding_id: str
    score: int
    label: str


class ScoreReportCommand(TypedDict):
    """Input: the items to score and order."""

    scan_id: str
    items: tuple[ScoreItem, ...]


class ScoreReportResult(TypedDict):
    """Output: the global score and the fix-first ordering."""

    scan_id: str
    score: int
    label: str
    ordered: tuple[ScoredItem, ...]


class ScoreReportServicePort(ABC):
    """Deterministic scoring — everything the SLM must never decide."""

    @abstractmethod
    def score(self, command: ScoreReportCommand) -> ScoreReportResult:
        """Return the global score and the fix-first ordering."""
        raise NotImplementedError  # pragma: no cover
