"""Tests for the DependencyRisk inventory aggregate (context: dependency_risk, SEC-13)."""

from __future__ import annotations

from hexa_sec.domain.dependency_risk.dependency import Dependency, DependencyFinding
from hexa_sec.domain.dependency_risk.dependency_risk import DependencyRisk
from hexa_sec.domain.dependency_risk.ecosystem import Ecosystem
from hexa_sec.domain.finding.severity import Severity


def _finding(
    package: str = "express",
    version: str = "4.17.1",
    cve: str = "CVE-2022-24999",
    severity: Severity = Severity.CRITICAL,
    evidence: str | None = None,
) -> DependencyFinding:
    return DependencyFinding(
        dependency=Dependency(package=package, version=version, ecosystem=Ecosystem.NPM),
        cve=cve,
        severity=severity,
        evidence=evidence if evidence is not None else f"lockfile:{package}@{version}",
    )


def test_for_asset_consolidates_findings() -> None:
    findings = (
        _finding(package="express", version="4.17.1", cve="CVE-2022-24999"),
        _finding(package="lodash", version="4.17.21", cve="CVE-2021-23337"),
        _finding(package="hexo", version="6.3.0", cve="CVE-2021-28858"),
    )
    risk = DependencyRisk.for_asset("acme/api", findings)
    assert risk.asset == "acme/api"
    assert len(risk.findings) == 3
    assert risk.vulnerable_count == 3
    assert risk.critical_count == 3


def test_for_asset_deduplicates_identical_findings() -> None:
    findings = (
        _finding(cve="CVE-2022-24999", evidence="a"),
        _finding(cve="CVE-2022-24999", evidence="b"),
    )
    risk = DependencyRisk.for_asset("acme/api", findings)
    assert len(risk.findings) == 1


def test_for_asset_tracks_versions_separately() -> None:
    findings = (
        _finding(package="express", version="4.17.1", cve="CVE-2022-24999"),
        _finding(package="express", version="4.18.0", cve="CVE-2022-24999"),
    )
    risk = DependencyRisk.for_asset("acme/api", findings)
    assert len(risk.findings) == 2


def test_for_asset_no_findings_returns_empty() -> None:
    risk = DependencyRisk.for_asset("acme/api", ())
    assert risk.findings == ()
    assert risk.vulnerable_count == 0
    assert risk.critical_count == 0


def test_for_asset_critical_count_only_critical() -> None:
    findings = (
        _finding(package="express", severity=Severity.CRITICAL),
        _finding(package="lodash", cve="CVE-2021-23337", severity=Severity.MEDIUM),
        _finding(package="numpy", version="1.21.0", severity=Severity.LOW),
    )
    risk = DependencyRisk.for_asset("acme/api", findings)
    assert risk.critical_count == 1
    assert risk.vulnerable_count == 3


def test_for_asset_is_deterministic() -> None:
    findings = (
        _finding(package="express", severity=Severity.CRITICAL),
        _finding(package="lodash", cve="CVE-2021-23337", severity=Severity.MEDIUM),
    )
    first = DependencyRisk.for_asset("acme/api", findings)
    second = DependencyRisk.for_asset("acme/api", findings)
    assert first == second
    assert first.critical_count == second.critical_count


# --- Category: concurrence / ordre (dedup max-sévérité, indépendant de l'ordre) ---


def test_for_asset_dedup_keeps_highest_severity() -> None:
    first = _finding(severity=Severity.HIGH, evidence="a")
    second = _finding(severity=Severity.CRITICAL, evidence="b")
    risk = DependencyRisk.for_asset("acme/api", (first, second))
    assert len(risk.findings) == 1
    assert risk.findings[0].severity is Severity.CRITICAL


def test_for_asset_dedup_order_independent_for_severity() -> None:
    high = _finding(severity=Severity.HIGH, evidence="a")
    critical = _finding(severity=Severity.CRITICAL, evidence="b")
    first = DependencyRisk.for_asset("acme/api", (high, critical))
    second = DependencyRisk.for_asset("acme/api", (critical, high))
    assert first == second
    assert first.findings[0].severity is Severity.CRITICAL
