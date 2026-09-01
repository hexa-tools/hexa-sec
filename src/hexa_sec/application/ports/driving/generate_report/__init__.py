"""Driving port for US-5 — generate_report."""

from __future__ import annotations

from hexa_sec.application.ports.driving.generate_report.generate_report_service_port import (
    GenerateReportCommand,
    GenerateReportResult,
    GenerateReportServicePort,
)

__all__ = ["GenerateReportCommand", "GenerateReportResult", "GenerateReportServicePort"]
