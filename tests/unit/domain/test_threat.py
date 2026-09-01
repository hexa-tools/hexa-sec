"""Tests for Threat (context: threat_intel, SEC-20)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.asset.asset import AssetId
from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.threat_intel.ioc import Ioc, IocType
from hexa_sec.domain.threat_intel.threat import Threat
from hexa_sec.domain.threat_intel.threat_actor import ThreatActor


def _threat(
    actor: ThreatActor = ThreatActor("APT-41", "Ransomware group"),
    tactic: str = "initial_access",
    severity: Severity = Severity.CRITICAL,
    assets: tuple[AssetId, ...] = (),
    findings: tuple[FindingId, ...] = (),
) -> Threat:
    return Threat(
        actor=actor,
        tactic=tactic,
        severity=severity,
        related_assets=assets,
        related_findings=findings,
    )


def test_threat_creation() -> None:
    threat = _threat()
    assert threat.actor.identifier == "APT-41"
    assert threat.tactic == "initial_access"
    assert threat.severity is Severity.CRITICAL
    assert threat.related_assets == ()
    assert threat.related_findings == ()


def test_threat_rejects_non_actor() -> None:
    with pytest.raises(ValueError):
        Threat(
            actor="APT-41",
            tactic="initial_access",
            severity=Severity.CRITICAL,
        )


def test_threat_rejects_empty_tactic() -> None:
    with pytest.raises(ValueError):
        _threat(tactic="")


def test_threat_rejects_blank_tactic() -> None:
    with pytest.raises(ValueError):
        _threat(tactic="   ")


def test_threat_rejects_non_severity() -> None:
    with pytest.raises(ValueError):
        Threat(
            actor=ThreatActor("APT-41", "Ransomware group"),
            tactic="initial_access",
            severity="critical",
        )


def test_threat_normalizes_tactic() -> None:
    assert _threat(tactic="  initial_access  ").tactic == "initial_access"


def test_threat_accepts_no_related() -> None:
    assert _threat().related_assets == ()


def test_threat_rejects_assets_without_finding_proof() -> None:
    with pytest.raises(ValueError):
        _threat(assets=(AssetId("payment-api"),))


def test_threat_accepts_assets_with_finding_proof() -> None:
    threat = _threat(assets=(AssetId("payment-api"),), findings=(FindingId("cve-2024-1234"),))
    assert threat.related_assets == (AssetId("payment-api"),)
    assert threat.related_findings == (FindingId("cve-2024-1234"),)
