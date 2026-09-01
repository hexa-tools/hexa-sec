"""CorrelateServicePort — the product's core (US-2)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class CorrelateCommand(TypedDict):
    """Input: the scan whose findings should be crossed."""

    scan_id: str


class CorrelateResult(TypedDict):
    """Output: the correlations found, each with its source findings (evidence)."""

    scan_id: str
    correlations: list[dict[str, str]]


class CorrelateServicePort(ABC):
    """Deterministic crossing of findings into insights. Never speculative."""

    @abstractmethod
    def correlate(self, command: CorrelateCommand) -> CorrelateResult:
        """Return the correlations for the scan."""
        raise NotImplementedError  # pragma: no cover
