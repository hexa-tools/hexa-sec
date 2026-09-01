"""Tests for GenerateReportServicePort (driving port — US-5)."""

from __future__ import annotations

import inspect

from hexa_sec.application.ports.driving.generate_report.generate_report_service_port import (
    GenerateReportServicePort,
)


def test_generate_report_service_port_is_abstract() -> None:
    assert inspect.isabstract(GenerateReportServicePort) is True
