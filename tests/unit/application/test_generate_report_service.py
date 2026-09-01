"""Tests for GenerateReportService (US-5 orchestration stub)."""

from __future__ import annotations

import pytest

from hexa_sec.application.ports.driving.generate_report.generate_report_service_port import (
    GenerateReportCommand,
)
from hexa_sec.application.service.generate_report_service import GenerateReportService


def test_generate_report_service_is_not_implemented() -> None:
    service = GenerateReportService()
    command: GenerateReportCommand = {"scan_id": "scan_0001"}
    with pytest.raises(NotImplementedError):
        service.generate(command)
