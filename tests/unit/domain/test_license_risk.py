"""Tests for License, LicenseRiskLevel and LicenseRisk (context: dependency_risk, SEC-13)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.dependency_risk.license_risk import (
    License,
    LicenseRisk,
    LicenseRiskLevel,
)


def test_license_normalizes_identifier() -> None:
    assert License("  MIT  ").identifier == "MIT"


def test_license_rejects_empty() -> None:
    with pytest.raises(ValueError):
        License("")
    with pytest.raises(ValueError):
        License("   ")


def test_license_risk_level_rank() -> None:
    assert LicenseRiskLevel.PERMISSIVE.rank < LicenseRiskLevel.UNKNOWN.rank
    assert LicenseRiskLevel.UNKNOWN.rank < LicenseRiskLevel.COPYLEFT.rank


def test_license_risk_level_risky_only_copyleft() -> None:
    assert LicenseRiskLevel.COPYLEFT.is_risky is True
    assert LicenseRiskLevel.PERMISSIVE.is_risky is False
    assert LicenseRiskLevel.UNKNOWN.is_risky is False


def test_license_risk_for_permissive_license() -> None:
    risk = LicenseRisk.for_identifier("MIT")
    assert risk.level is LicenseRiskLevel.PERMISSIVE
    assert risk.license is not None
    assert risk.license.identifier == "MIT"


def test_license_risk_for_copyleft_is_high() -> None:
    risk = LicenseRisk.for_identifier("GPL-3.0")
    assert risk.level is LicenseRiskLevel.COPYLEFT
    assert risk.level.is_risky is True


def test_license_risk_for_unknown_non_empty() -> None:
    risk = LicenseRisk.for_identifier("Weird-1.0")
    assert risk.level is LicenseRiskLevel.UNKNOWN
    assert risk.license is not None


def test_license_risk_for_absent_is_unknown() -> None:
    risk = LicenseRisk.for_identifier(None)
    assert risk.level is LicenseRiskLevel.UNKNOWN
    assert risk.license is None


def test_license_risk_never_guesses_unknown() -> None:
    assert LicenseRisk.for_identifier("nonsense").level is LicenseRiskLevel.UNKNOWN
