"""Tests for ScoreReportService (US-3 orchestration stub)."""

from __future__ import annotations

import pytest

from hexa_sec.application.ports.driving.score_report.score_report_service_port import ScoreReportCommand
from hexa_sec.application.service.score_report_service import ScoreReportService


def test_score_report_service_is_not_implemented() -> None:
    service = ScoreReportService()
    command: ScoreReportCommand = {"scan_id": "scan_0001"}
    with pytest.raises(NotImplementedError):
        service.score(command)
