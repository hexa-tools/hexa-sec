"""GenerateReportUseCase — application entry for the deliverable (US-5)."""

from __future__ import annotations

from hexa_sec.application.ports.driving.generate_report.generate_report_service_port import (
    GenerateReportCommand,
    GenerateReportResult,
    GenerateReportServicePort,
)


class GenerateReportUseCase(GenerateReportServicePort):
    """Depends on the service ABC so it is mockable per test."""

    def __init__(self, service: GenerateReportServicePort) -> None:
        self._service = service

    def generate(self, command: GenerateReportCommand) -> GenerateReportResult:
        return self._service.generate(command)
