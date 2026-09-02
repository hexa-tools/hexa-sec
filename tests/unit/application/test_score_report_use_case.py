"""Tests for ScoreReportUseCase (US-3)."""

from __future__ import annotations

from hexa_sec.application.ports.driving.score_report.score_report_service_port import (
    ScoreReportCommand,
    ScoreReportServicePort,
)
from hexa_sec.application.use_case.score_report.score_report_use_case import ScoreReportUseCase


class _Stub(ScoreReportServicePort):
    def score(self, command: ScoreReportCommand) -> dict[str, object]:
        return {"scan_id": command["scan_id"], "score": 62, "label": "moderate", "ordered": ()}


def test_score_report_use_case_delegates_to_service() -> None:
    use_case = ScoreReportUseCase(_Stub())
    command: ScoreReportCommand = {"scan_id": "scan_0001", "items": ()}
    result = use_case.score(command)
    assert result["scan_id"] == "scan_0001"
    assert result["score"] == 62
    assert result["label"] == "moderate"
