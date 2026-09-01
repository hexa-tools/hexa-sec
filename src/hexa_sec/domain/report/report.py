"""Report — the deliverable outline (context: report, skeleton)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReportId:
    """An absolute identifier for a report."""

    value: str


@dataclass(frozen=True)
class Report:
    """Top-level report shell. Five sections are filled in Phase 6 (US-5)."""

    report_id: ReportId
    title: str

    def __post_init__(self) -> None:
        if not self.title:
            raise ValueError("report title cannot be empty")
