"""ScoreReportService — deterministic fix-first ordering (US-3, scaffold)."""

from __future__ import annotations

from hexa_sec.application.ports.driving.score_report.score_report_service_port import (
    ScoreReportCommand,
    ScoreReportResult,
    ScoreReportServicePort,
)


class ScoreReportService(ScoreReportServicePort):
    """Score and order (bootstrap stub)."""

    def score(self, command: ScoreReportCommand) -> ScoreReportResult:
        raise NotImplementedError  # pragma: no cover
