"""Tests for Report (context: report)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.report.report import Report, ReportId


def test_report_creation() -> None:
    report = Report(report_id=ReportId("rep_0001"), title="Audit report")
    assert report.title == "Audit report"


def test_report_rejects_empty_title() -> None:
    with pytest.raises(ValueError):
        Report(report_id=ReportId("rep_0002"), title="")
