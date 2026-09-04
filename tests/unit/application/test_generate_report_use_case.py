"""Tests for GenerateReportUseCase (US-5)."""

from __future__ import annotations

from hexa_sec.application.ports.driving.generate_report.generate_report_service_port import (
    GenerateReportCommand,
)
from hexa_sec.application.service.generate_report_service import GenerateReportService
from hexa_sec.application.use_case.generate_report.generate_report_use_case import (
    GenerateReportUseCase,
)


def _command() -> GenerateReportCommand:
    return GenerateReportCommand(
        scan_id="scan_0001",
        tenant_id="tnt_0001",
        title="Audit Acme",
        score=62,
        previous_score=None,
        ai_summary="",
        actions=(),
        correlations=(),
        findings=(),
        compliance=(),
    )


def test_generate_report_use_case_delegates_to_service() -> None:
    use_case = GenerateReportUseCase(GenerateReportService())
    result = use_case.generate(_command())
    assert result["report_id"] == "rep_scan_0001"
    assert result["markdown"].startswith("# Audit Acme")
    assert "## 1. Score global" in result["markdown"]
