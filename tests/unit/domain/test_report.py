"""Tests for ReportId + Report (context: report, SEC-8)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.finding.finding import Finding, FindingId
from hexa_sec.domain.report.priority_action import PriorityAction
from hexa_sec.domain.report.report import Report, ReportId
from hexa_sec.domain.report.report_section import ReportSection
from hexa_sec.domain.scoring.risk_score import RiskScore


def _action() -> PriorityAction:
    return PriorityAction(
        finding_id=FindingId("fnd_0001"),
        issue="Exposed API key",
        why="Account takeover risk",
        fix="Rotate the key",
        effort="5 min",
        risk_score=RiskScore.from_value(95.0),
    )


def test_report_creation() -> None:
    report = Report(report_id=ReportId("rep_0001"), title="Audit report")
    assert report.title == "Audit report"
    assert report.top_actions == ()
    assert report.global_score is None


def test_report_rejects_empty_title() -> None:
    with pytest.raises(ValueError):
        Report(report_id=ReportId("rep_0002"), title="")


def test_report_rejects_whitespace_title() -> None:
    with pytest.raises(ValueError):
        Report(report_id=ReportId("rep_0003"), title="   ")


def test_report_id_rejects_empty_value() -> None:
    with pytest.raises(ValueError):
        ReportId("")


def test_report_allows_empty_sections() -> None:
    # rapport sans finding : les sections vides sont rendues, pas un échec.
    report = Report(report_id=ReportId("rep_0004"), title="Audit")
    assert report.top_actions == ()
    assert report.correlations == ()
    assert report.detail == ()
    assert report.compliance == ()


def test_report_top_actions_no_more_than_five() -> None:
    actions = tuple(_action() for _ in range(5))
    report = Report(report_id=ReportId("rep_0005"), title="Audit", top_actions=actions)
    assert len(report.top_actions) == 5


def test_report_rejects_more_than_five_top_actions() -> None:
    actions = tuple(_action() for _ in range(6))
    with pytest.raises(ValueError):
        Report(report_id=ReportId("rep_0006"), title="Audit", top_actions=actions)


def test_report_sections_in_canonical_order() -> None:
    report = Report(report_id=ReportId("rep_0007"), title="Audit")
    assert report.sections() == (
        ReportSection.SCORE,
        ReportSection.TOP_FIVE,
        ReportSection.CORRELATIONS,
        ReportSection.DETAIL,
        ReportSection.COMPLIANCE,
    )
