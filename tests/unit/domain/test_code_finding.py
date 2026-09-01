"""Tests for CodeFinding (context: code_risk, SEC-14)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.code_risk.code_finding import CodeFinding
from hexa_sec.domain.code_risk.code_location import CodeLocation
from hexa_sec.domain.code_risk.rule_id import RuleId
from hexa_sec.domain.finding.severity import Severity


def _finding(
    asset: str = "acme/api",
    rule_id: RuleId = RuleId("bandit.B101", "Assert used"),
    severity: Severity = Severity.HIGH,
    evidence: str = "assert x == 1",
) -> CodeFinding:
    return CodeFinding(
        asset=asset,
        rule_id=rule_id,
        location=CodeLocation(file="src/app.py", line=42),
        severity=severity,
        evidence=evidence,
    )


def test_code_finding_creation() -> None:
    finding = _finding()
    assert finding.asset == "acme/api"
    assert finding.rule_id.identifier == "bandit.B101"
    assert finding.location.file == "src/app.py"
    assert finding.location.line == 42
    assert finding.severity is Severity.HIGH
    assert finding.evidence == "assert x == 1"


def test_code_finding_rejects_empty_asset() -> None:
    with pytest.raises(ValueError):
        _finding(asset="")


def test_code_finding_rejects_blank_asset() -> None:
    with pytest.raises(ValueError):
        _finding(asset="   ")


def test_code_finding_rejects_non_rule_id() -> None:
    with pytest.raises(ValueError):
        CodeFinding(
            asset="acme/api",
            rule_id="bandit.B101",
            location=CodeLocation(file="src/app.py", line=42),
            severity=Severity.HIGH,
            evidence="assert x == 1",
        )


def test_code_finding_rejects_non_location() -> None:
    with pytest.raises(ValueError):
        CodeFinding(
            asset="acme/api",
            rule_id=RuleId("bandit.B101", "Assert used"),
            location="src/app.py:42",
            severity=Severity.HIGH,
            evidence="assert x == 1",
        )


def test_code_finding_rejects_non_severity() -> None:
    with pytest.raises(ValueError):
        CodeFinding(
            asset="acme/api",
            rule_id=RuleId("bandit.B101", "Assert used"),
            location=CodeLocation(file="src/app.py", line=42),
            severity="high",
            evidence="assert x == 1",
        )


def test_code_finding_rejects_empty_evidence() -> None:
    with pytest.raises(ValueError):
        _finding(evidence="")


def test_code_finding_rejects_blank_evidence() -> None:
    with pytest.raises(ValueError):
        _finding(evidence="   ")
