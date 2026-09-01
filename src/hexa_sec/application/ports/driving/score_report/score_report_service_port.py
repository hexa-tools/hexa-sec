"""ScoreReportServicePort — scoring and ordering (US-3)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class ScoreReportCommand(TypedDict):
    """Input: the scan to score."""

    scan_id: str


class ScoreReportResult(TypedDict):
    """Output: the deterministic fix-first ordering."""

    scan_id: str
    score: int
    label: str


class ScoreReportServicePort(ABC):
    """Deterministic scoring — everything the SLM must never decide."""

    @abstractmethod
    def score(self, command: ScoreReportCommand) -> ScoreReportResult:
        """Return the global score and fix-first ordering."""
        raise NotImplementedError  # pragma: no cover
