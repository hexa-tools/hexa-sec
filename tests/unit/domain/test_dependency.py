"""Tests for Dependency and DependencyFinding (context: dependency_risk, SEC-13)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.dependency_risk.dependency import Dependency, DependencyFinding
from hexa_sec.domain.dependency_risk.ecosystem import Ecosystem
from hexa_sec.domain.finding.severity import Severity


def _dependency(
    package: str = "express",
    version: str = "4.17.1",
    ecosystem: Ecosystem = Ecosystem.NPM,
) -> Dependency:
    return Dependency(package=package, version=version, ecosystem=ecosystem)


def test_dependency_creation() -> None:
    dep = _dependency()
    assert dep.package == "express"
    assert dep.version == "4.17.1"
    assert dep.ecosystem is Ecosystem.NPM


def test_dependency_rejects_empty_package() -> None:
    with pytest.raises(ValueError):
        _dependency(package="")


def test_dependency_rejects_whitespace_package() -> None:
    with pytest.raises(ValueError):
        _dependency(package="   ")


def test_dependency_rejects_empty_version() -> None:
    with pytest.raises(ValueError):
        _dependency(version="")


def test_dependency_rejects_blank_version() -> None:
    with pytest.raises(ValueError):
        _dependency(version="   ")


def test_dependency_rejects_non_ecosystem() -> None:
    with pytest.raises(ValueError):
        Dependency(package="express", version="1.0.0", ecosystem="npm")


def test_dependency_finding_creation() -> None:
    finding = DependencyFinding(
        dependency=_dependency(),
        cve="CVE-2022-24999",
        severity=Severity.CRITICAL,
        evidence="lockfile: express@4.17.1",
    )
    assert finding.dependency.package == "express"
    assert finding.cve == "CVE-2022-24999"
    assert finding.severity is Severity.CRITICAL
    assert finding.evidence == "lockfile: express@4.17.1"


def test_dependency_finding_rejects_empty_cve() -> None:
    with pytest.raises(ValueError):
        DependencyFinding(
            dependency=_dependency(),
            cve="",
            severity=Severity.HIGH,
            evidence="lockfile: express@4.17.1",
        )


def test_dependency_finding_rejects_blank_evidence() -> None:
    with pytest.raises(ValueError):
        DependencyFinding(
            dependency=_dependency(),
            cve="CVE-2022-24999",
            severity=Severity.HIGH,
            evidence="   ",
        )


def test_dependency_finding_rejects_non_severity() -> None:
    with pytest.raises(ValueError):
        DependencyFinding(
            dependency=_dependency(),
            cve="CVE-2022-24999",
            severity="high",
            evidence="lockfile",
        )


def test_dependency_finding_rejects_non_dependency() -> None:
    with pytest.raises(ValueError):
        DependencyFinding(
            dependency="express@4.17.1",
            cve="CVE-2022-24999",
            severity=Severity.HIGH,
            evidence="lockfile",
        )
