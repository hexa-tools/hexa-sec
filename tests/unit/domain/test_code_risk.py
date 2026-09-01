"""Tests for the CodeRisk inventory aggregate (context: code_risk, SEC-14)."""

from __future__ import annotations

from hexa_sec.domain.code_risk.code_finding import CodeFinding
from hexa_sec.domain.code_risk.code_location import CodeLocation
from hexa_sec.domain.code_risk.code_risk import CodeRisk
from hexa_sec.domain.code_risk.rule_id import RuleId
from hexa_sec.domain.finding.severity import Severity


def _finding(
    asset: str = "acme/api",
    rule_id: RuleId = RuleId("bandit.B101", "Assert used"),
    file: str = "src/app.py",
    line: int = 42,
    severity: Severity = Severity.HIGH,
    evidence: str = "assert x == 1",
) -> CodeFinding:
    return CodeFinding(
        asset=asset,
        rule_id=rule_id,
        location=CodeLocation(file=file, line=line),
        severity=severity,
        evidence=evidence,
    )


def test_for_asset_consolidates_findings() -> None:
    findings = (
        _finding(rule_id=RuleId("bandit.B101", "Assert used"), line=42),
        _finding(rule_id=RuleId("bandit.B307", "Hardcoded password"), line=10),
        _finding(rule_id=RuleId("semgrep.py.eval", "Use of eval"), line=7),
    )
    risk = CodeRisk.for_asset("acme/api", findings)
    assert risk.asset == "acme/api"
    assert len(risk.findings) == 3
    assert risk.risk_count == 3
    assert risk.critical_count == 0


def test_for_asset_deduplicates_identical_findings() -> None:
    findings = (_finding(), _finding())
    risk = CodeRisk.for_asset("acme/api", findings)
    assert len(risk.findings) == 1


def test_for_asset_keeps_distinct_locations_separate() -> None:
    findings = (
        _finding(line=10, evidence="a"),
        _finding(line=99, evidence="b"),
    )
    risk = CodeRisk.for_asset("acme/api", findings)
    assert len(risk.findings) == 2


def test_for_asset_keeps_low_severity_finding() -> None:
    benign = _finding(severity=Severity.LOW, evidence="a")
    risk = CodeRisk.for_asset("acme/api", (benign,))
    assert len(risk.findings) == 1
    assert risk.findings[0].severity is Severity.LOW


def test_for_asset_ignores_findings_of_other_asset() -> None:
    risk = CodeRisk.for_asset("acme/api", (_finding(asset="other/repo"),))
    assert risk.findings == ()
    assert risk.risk_count == 0


def test_for_asset_no_findings_returns_empty() -> None:
    risk = CodeRisk.for_asset("acme/api", ())
    assert risk.findings == ()
    assert risk.risk_count == 0
    assert risk.critical_count == 0


def test_for_asset_critical_count_only_critical() -> None:
    findings = (
        _finding(severity=Severity.CRITICAL, line=1),
        _finding(severity=Severity.MEDIUM, line=2),
        _finding(severity=Severity.LOW, line=3),
    )
    risk = CodeRisk.for_asset("acme/api", findings)
    assert risk.critical_count == 1
    assert risk.risk_count == 3


def test_for_asset_is_deterministic() -> None:
    findings = (
        _finding(severity=Severity.CRITICAL, line=1),
        _finding(severity=Severity.MEDIUM, line=2),
    )
    first = CodeRisk.for_asset("acme/api", findings)
    second = CodeRisk.for_asset("acme/api", findings)
    assert first == second
    assert first.critical_count == second.critical_count


# --- Category: concurrence / ordre (dedup max-sévérité, indépendant de l'ordre) ---


def test_for_asset_dedup_keeps_highest_severity() -> None:
    first = _finding(severity=Severity.MEDIUM, evidence="a")
    second = _finding(severity=Severity.CRITICAL, evidence="b")
    risk = CodeRisk.for_asset("acme/api", (first, second))
    assert len(risk.findings) == 1
    assert risk.findings[0].severity is Severity.CRITICAL


def test_for_asset_dedup_order_independent_for_severity() -> None:
    medium = _finding(severity=Severity.MEDIUM, evidence="a")
    critical = _finding(severity=Severity.CRITICAL, evidence="b")
    first = CodeRisk.for_asset("acme/api", (medium, critical))
    second = CodeRisk.for_asset("acme/api", (critical, medium))
    assert first == second
    assert first.findings[0].severity is Severity.CRITICAL


# --- Category: stabilité / déterminisme (tie-break sur evidence) ------------


def test_for_asset_dedup_same_severity_keeps_smallest_evidence() -> None:
    a = _finding(severity=Severity.HIGH, evidence="weak-password")
    b = _finding(severity=Severity.HIGH, evidence="hardcoded-secret")
    risk = CodeRisk.for_asset("acme/api", (a, b))
    assert len(risk.findings) == 1
    assert risk.findings[0].evidence == "hardcoded-secret"


def test_for_asset_dedup_order_independent_for_evidence() -> None:
    a = _finding(severity=Severity.HIGH, evidence="weak-password")
    b = _finding(severity=Severity.HIGH, evidence="hardcoded-secret")
    first = CodeRisk.for_asset("acme/api", (a, b))
    second = CodeRisk.for_asset("acme/api", (b, a))
    assert first == second
    assert first.findings[0].evidence == second.findings[0].evidence
