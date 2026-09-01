"""GenerateReportServicePort — the client deliverable (US-5)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypedDict


class GenerateReportCommand(TypedDict):
    """Input: the scan to report."""

    scan_id: str


class GenerateReportResult(TypedDict):
    """Output: the markdown report."""

    report_id: str
    markdown: str


class GenerateReportServicePort(ABC):
    """Produce the 5-section report, with the SLM only writing the opening."""

    @abstractmethod
    def generate(self, command: GenerateReportCommand) -> GenerateReportResult:
        """Return the report for the scan."""
        raise NotImplementedError  # pragma: no cover
