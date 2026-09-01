"""GenerateReportService — the client deliverable (US-5, scaffold)."""

from __future__ import annotations

from hexa_sec.application.ports.driving.generate_report.generate_report_service_port import (
    GenerateReportCommand,
    GenerateReportResult,
    GenerateReportServicePort,
)


class GenerateReportService(GenerateReportServicePort):
    """Produce the 5-section report (bootstrap stub)."""

    def generate(self, command: GenerateReportCommand) -> GenerateReportResult:
        raise NotImplementedError  # pragma: no cover
