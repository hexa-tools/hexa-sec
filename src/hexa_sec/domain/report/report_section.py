"""ReportSection — the five ordered sections of a report (context: report)."""

from __future__ import annotations

from enum import Enum


class ReportSection(Enum):
    """The audit deliverable's five sections, in the client-facing order."""

    SCORE = "score"
    TOP_FIVE = "top_five"
    CORRELATIONS = "correlations"
    DETAIL = "detail"
    COMPLIANCE = "compliance"

    @property
    def order(self) -> int:
        return {
            ReportSection.SCORE: 1,
            ReportSection.TOP_FIVE: 2,
            ReportSection.CORRELATIONS: 3,
            ReportSection.DETAIL: 4,
            ReportSection.COMPLIANCE: 5,
        }[self]
