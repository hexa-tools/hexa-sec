"""ScoreReportUseCase — application entry for deterministic scoring (US-3)."""

from __future__ import annotations

from hexa_sec.application.ports.driving.score_report.score_report_service_port import (
    ScoreReportCommand,
    ScoreReportResult,
    ScoreReportServicePort,
)


class ScoreReportUseCase(ScoreReportServicePort):
    """Depends on the service ABC so it is mockable per test."""

    def __init__(self, service: ScoreReportServicePort) -> None:
        self._service = service

    def score(self, command: ScoreReportCommand) -> ScoreReportResult:
        return self._service.score(command)
