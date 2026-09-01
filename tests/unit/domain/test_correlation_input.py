"""Tests for CorrelationInput (context: correlation)."""

from __future__ import annotations

from hexa_sec.domain.asset.asset import AssetId
from hexa_sec.domain.correlation.correlation_input import CorrelationInput
from hexa_sec.domain.correlation.finding_kind import FindingKind
from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.finding.severity import Severity


def test_correlation_input_creation() -> None:
    signal = CorrelationInput(
        finding_id=FindingId("fnd_0001"),
        assets=(AssetId("ast_0001"),),
        kind=FindingKind.VULNERABILITY,
        severity=Severity.CRITICAL,
        detail="CVE-2024-0001 RCE",
    )
    assert signal.kind is FindingKind.VULNERABILITY
    assert signal.severity is Severity.CRITICAL
    assert signal.detail == "CVE-2024-0001 RCE"


def test_correlation_input_defaults_empty_assets() -> None:
    signal = CorrelationInput(finding_id=FindingId("fnd_0001"), kind=FindingKind.NOISE, severity=Severity.LOW)
    assert signal.assets == ()
