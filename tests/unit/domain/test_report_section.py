"""Tests for ReportSection (context: report, SEC-8)."""

from __future__ import annotations

from hexa_sec.domain.report.report_section import ReportSection


def test_report_section_members() -> None:
    assert ReportSection.SCORE.value == "score"
    assert ReportSection.TOP_FIVE.value == "top_five"
    assert ReportSection.CORRELATIONS.value == "correlations"
    assert ReportSection.DETAIL.value == "detail"
    assert ReportSection.COMPLIANCE.value == "compliance"


def test_report_section_orders_ascending() -> None:
    orders = [ReportSection.SCORE, ReportSection.TOP_FIVE, ReportSection.CORRELATIONS, ReportSection.DETAIL, ReportSection.COMPLIANCE]
    assert [section.order for section in orders] == [1, 2, 3, 4, 5]


def test_report_section_order_is_strict() -> None:
    assert ReportSection.SCORE.order < ReportSection.TOP_FIVE.order
    assert ReportSection.TOP_FIVE.order < ReportSection.CORRELATIONS.order
    assert ReportSection.CORRELATIONS.order < ReportSection.DETAIL.order
    assert ReportSection.DETAIL.order < ReportSection.COMPLIANCE.order
