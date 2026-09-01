"""Tests for the ConfigRisk inventory aggregate (context: config_risk, SEC-15)."""

from __future__ import annotations

from hexa_sec.domain.config_risk.benchmark_id import BenchmarkId
from hexa_sec.domain.config_risk.config_check import ConfigCheck
from hexa_sec.domain.config_risk.config_finding import ConfigFinding
from hexa_sec.domain.config_risk.config_risk import ConfigRisk
from hexa_sec.domain.finding.severity import Severity

_BENCHMARK = BenchmarkId("cis_ubuntu_22.04", "CIS Ubuntu 22.04")


def _finding(
    asset: str = "srv-01",
    check: str = "1.1.1",
    severity: Severity = Severity.HIGH,
    evidence: str = "unexpected: world-writable",
) -> ConfigFinding:
    return ConfigFinding(
        asset=asset,
        benchmark_id=_BENCHMARK,
        check=ConfigCheck(check),
        severity=severity,
        evidence=evidence,
    )


def test_for_asset_consolidates_findings() -> None:
    findings = (
        _finding(check="1.1.1"),
        _finding(check="1.2.1", severity=Severity.MEDIUM),
        _finding(check="5.1.1", severity=Severity.LOW),
    )
    risk = ConfigRisk.for_asset("srv-01", findings)
    assert risk.asset == "srv-01"
    assert len(risk.findings) == 3
    assert risk.gap_count == 3
    assert risk.critical_count == 0


def test_for_asset_deduplicates_identical_findings() -> None:
    findings = (_finding(), _finding())
    risk = ConfigRisk.for_asset("srv-01", findings)
    assert len(risk.findings) == 1


def test_for_asset_keeps_distinct_checks_separate() -> None:
    findings = (
        _finding(check="1.1.1", evidence="a"),
        _finding(check="1.1.2", evidence="b"),
    )
    risk = ConfigRisk.for_asset("srv-01", findings)
    assert len(risk.findings) == 2


def test_for_asset_keeps_tolerable_low_severity_gap() -> None:
    tolerable = _finding(severity=Severity.LOW)
    risk = ConfigRisk.for_asset("srv-01", (tolerable,))
    assert len(risk.findings) == 1
    assert risk.findings[0].severity is Severity.LOW


def test_for_asset_ignores_findings_of_other_asset() -> None:
    risk = ConfigRisk.for_asset("srv-01", (_finding(asset="srv-02"),))
    assert risk.findings == ()
    assert risk.gap_count == 0


def test_for_asset_no_findings_returns_empty() -> None:
    risk = ConfigRisk.for_asset("srv-01", ())
    assert risk.findings == ()
    assert risk.gap_count == 0
    assert risk.critical_count == 0


def test_for_asset_critical_count_only_critical() -> None:
    findings = (
        _finding(check="1.1.1", severity=Severity.CRITICAL),
        _finding(check="1.2.1", severity=Severity.MEDIUM),
        _finding(check="5.1.1", severity=Severity.INFO),
    )
    risk = ConfigRisk.for_asset("srv-01", findings)
    assert risk.critical_count == 1
    assert risk.gap_count == 3


def test_for_asset_is_deterministic() -> None:
    findings = (
        _finding(check="1.1.1", severity=Severity.CRITICAL),
        _finding(check="1.2.1", severity=Severity.MEDIUM),
    )
    first = ConfigRisk.for_asset("srv-01", findings)
    second = ConfigRisk.for_asset("srv-01", findings)
    assert first == second
    assert first.critical_count == second.critical_count


# --- Category: concurrence / ordre (dedup max-sévérité, indépendant de l'ordre) ---


def test_for_asset_dedup_keeps_highest_severity() -> None:
    first = _finding(severity=Severity.MEDIUM, evidence="a")
    second = _finding(severity=Severity.CRITICAL, evidence="b")
    risk = ConfigRisk.for_asset("srv-01", (first, second))
    assert len(risk.findings) == 1
    assert risk.findings[0].severity is Severity.CRITICAL


def test_for_asset_dedup_order_independent_for_severity() -> None:
    medium = _finding(severity=Severity.MEDIUM, evidence="a")
    critical = _finding(severity=Severity.CRITICAL, evidence="b")
    first = ConfigRisk.for_asset("srv-01", (medium, critical))
    second = ConfigRisk.for_asset("srv-01", (critical, medium))
    assert first == second
    assert first.findings[0].severity is Severity.CRITICAL


# --- Category: stabilité / déterminisme (tie-break sur evidence) ------------


def test_for_asset_dedup_same_severity_keeps_smallest_evidence() -> None:
    a = _finding(severity=Severity.HIGH, evidence="zzz")
    b = _finding(severity=Severity.HIGH, evidence="aaa")
    risk = ConfigRisk.for_asset("srv-01", (a, b))
    assert len(risk.findings) == 1
    assert risk.findings[0].evidence == "aaa"


def test_for_asset_dedup_order_independent_for_evidence() -> None:
    a = _finding(severity=Severity.HIGH, evidence="zzz")
    b = _finding(severity=Severity.HIGH, evidence="aaa")
    first = ConfigRisk.for_asset("srv-01", (a, b))
    second = ConfigRisk.for_asset("srv-01", (b, a))
    assert first == second
    assert first.findings[0].evidence == second.findings[0].evidence


# --- Category: stabilité / déterminisme (ordre total, multi-éléments) -------


def test_for_asset_dedup_complex_is_order_independent() -> None:
    c_zzz = _finding(severity=Severity.CRITICAL, evidence="zzz")
    c_aaa = _finding(severity=Severity.CRITICAL, evidence="aaa")
    h_bbb = _finding(severity=Severity.HIGH, evidence="bbb")
    evidences = {
        ConfigRisk.for_asset("srv-01", permutation).findings[0].evidence
        for permutation in _permutations((c_zzz, c_aaa, h_bbb))
    }
    assert evidences == {"aaa"}


def _permutations(values: tuple[ConfigFinding, ...]) -> list[tuple[ConfigFinding, ...]]:
    if len(values) <= 1:
        return [values]
    out: list[tuple[ConfigFinding, ...]] = []
    for index in range(len(values)):
        rest = values[:index] + values[index + 1 :]
        for tail in _permutations(rest):
            out.append((values[index],) + tail)
    return out
