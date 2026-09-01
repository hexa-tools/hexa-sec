"""Tests for ScoreReportUseCase (US-3)."""

from __future__ import annotations

import pytest

from hexa_sec.application.ports.driving.score_report.score_report_service_port import ScoreReportCommand
from hexa_sec.application.service.score_report_service import ScoreReportService
from hexa_sec.application.use_case.score_report.score_report_use_case import ScoreReportUseCase


def test_score_report_use_case_delegates_to_service() -> None:
    use_case = ScoreReportUseCase(ScoreReportService())
    command: ScoreReportCommand = {"scan_id": "scan_0001"}
    with pytest.raises(NotImplementedError):
        use_case.score(command)
