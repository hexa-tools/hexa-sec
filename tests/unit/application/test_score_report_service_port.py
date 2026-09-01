"""Tests for ScoreReportServicePort (driving port — US-3)."""

from __future__ import annotations

import inspect

from hexa_sec.application.ports.driving.score_report.score_report_service_port import ScoreReportServicePort


def test_score_report_service_port_is_abstract() -> None:
    assert inspect.isabstract(ScoreReportServicePort) is True
