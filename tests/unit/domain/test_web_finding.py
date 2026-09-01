"""Tests for WebFinding (context: web_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.web_risk.web_finding import WebFinding


def test_web_finding_creation() -> None:
    finding = WebFinding(asset="https://app.example", method="sql_injection")
    assert finding.method == "sql_injection"


def test_web_finding_rejects_empty_asset() -> None:
    with pytest.raises(ValueError):
        WebFinding(asset="", method="xss")


def test_web_finding_rejects_empty_method() -> None:
    with pytest.raises(ValueError):
        WebFinding(asset="https://app.example", method="")
