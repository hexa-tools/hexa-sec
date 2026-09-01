"""Tests for GenerateReportUseCase (US-5)."""

from __future__ import annotations

import pytest

from hexa_sec.application.ports.driving.generate_report.generate_report_service_port import (
    GenerateReportCommand,
)
from hexa_sec.application.service.generate_report_service import GenerateReportService
from hexa_sec.application.use_case.generate_report.generate_report_use_case import GenerateReportUseCase


def test_generate_report_use_case_delegates_to_service() -> None:
    use_case = GenerateReportUseCase(GenerateReportService())
    command: GenerateReportCommand = {"scan_id": "scan_0001"}
    with pytest.raises(NotImplementedError):
        use_case.generate(command)
