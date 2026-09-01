"""Tests for ReportStorePort (driven port)."""

from __future__ import annotations

import inspect

from hexa_sec.application.ports.driven.report_store_port import ReportStorePort


def test_report_store_port_is_abstract() -> None:
    assert inspect.isabstract(ReportStorePort) is True
