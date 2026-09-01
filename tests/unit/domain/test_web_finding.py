"""Tests for WebFinding (context: web_risk, SEC-10)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.web_risk.owasp_category import OwaspCategory
from hexa_sec.domain.web_risk.web_finding import WebFinding


def _finding(**overrides: object) -> WebFinding:
    defaults: dict[str, object] = {
        "asset": "https://app.example",
        "method": "sql_injection",
        "category": OwaspCategory.INJECTION,
        "severity": Severity.HIGH,
        "evidence": "GET /login?user=1' OR '1'='1",
    }
    defaults.update(overrides)
    return WebFinding(**defaults)


def test_web_finding_creation() -> None:
    finding = _finding()
    assert finding.method == "sql_injection"
    assert finding.category is OwaspCategory.INJECTION
    assert finding.severity is Severity.HIGH
    assert finding.evidence is not None


def test_web_finding_defaults_severity_medium() -> None:
    finding = WebFinding(
        asset="https://app.example",
        method="xss",
        category=OwaspCategory.INJECTION,
        evidence="<script>alert(1)</script>",
    )
    assert finding.severity is Severity.MEDIUM


def test_web_finding_rejects_empty_asset() -> None:
    with pytest.raises(ValueError):
        _finding(asset="")


def test_web_finding_rejects_whitespace_asset() -> None:
    with pytest.raises(ValueError):
        _finding(asset="   ")


def test_web_finding_rejects_empty_method() -> None:
    with pytest.raises(ValueError):
        _finding(method="")


def test_web_finding_requires_evidence() -> None:
    # pas de preuve -> rejeté (pas de spéculation)
    with pytest.raises(ValueError):
        _finding(evidence="")


def test_web_finding_rejects_whitespace_evidence() -> None:
    with pytest.raises(ValueError):
        _finding(evidence="   ")
