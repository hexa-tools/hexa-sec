"""Tests for ConfigFinding (context: config_risk, SEC-15)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.config_risk.benchmark_id import BenchmarkId
from hexa_sec.domain.config_risk.config_check import ConfigCheck
from hexa_sec.domain.config_risk.config_finding import ConfigFinding
from hexa_sec.domain.finding.severity import Severity

_BENCHMARK = BenchmarkId("cis_ubuntu_22.04", "CIS Ubuntu 22.04")


def _finding(
    asset: str = "srv-01",
    benchmark: BenchmarkId = _BENCHMARK,
    check: ConfigCheck = ConfigCheck("1.1.1"),
    severity: Severity = Severity.HIGH,
    evidence: str = "unexpected: world-writable",
) -> ConfigFinding:
    return ConfigFinding(
        asset=asset,
        benchmark_id=benchmark,
        check=check,
        severity=severity,
        evidence=evidence,
    )


def test_config_finding_creation() -> None:
    finding = _finding()
    assert finding.asset == "srv-01"
    assert finding.benchmark_id.identifier == "cis_ubuntu_22.04"
    assert finding.check.identifier == "1.1.1"
    assert finding.severity is Severity.HIGH
    assert finding.evidence == "unexpected: world-writable"


def test_config_finding_rejects_empty_asset() -> None:
    with pytest.raises(ValueError):
        _finding(asset="")


def test_config_finding_rejects_blank_asset() -> None:
    with pytest.raises(ValueError):
        _finding(asset="   ")


def test_config_finding_rejects_non_benchmark_id() -> None:
    with pytest.raises(ValueError):
        ConfigFinding(
            asset="srv-01",
            benchmark_id="cis_ubuntu_22.04",
            check=ConfigCheck("1.1.1"),
            severity=Severity.HIGH,
            evidence="unexpected: world-writable",
        )


def test_config_finding_rejects_non_config_check() -> None:
    with pytest.raises(ValueError):
        ConfigFinding(
            asset="srv-01",
            benchmark_id=_BENCHMARK,
            check="1.1.1",
            severity=Severity.HIGH,
            evidence="unexpected: world-writable",
        )


def test_config_finding_rejects_non_severity() -> None:
    with pytest.raises(ValueError):
        ConfigFinding(
            asset="srv-01",
            benchmark_id=_BENCHMARK,
            check=ConfigCheck("1.1.1"),
            severity="high",
            evidence="unexpected: world-writable",
        )


def test_config_finding_rejects_empty_evidence() -> None:
    with pytest.raises(ValueError):
        _finding(evidence="")


def test_config_finding_rejects_blank_evidence() -> None:
    with pytest.raises(ValueError):
        _finding(evidence="   ")
