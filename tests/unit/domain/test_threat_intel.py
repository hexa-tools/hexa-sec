"""Tests for the ThreatIntel aggregate (context: threat_intel, SEC-20)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.asset.asset import AssetId
from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.threat_intel.threat import Threat
from hexa_sec.domain.threat_intel.threat_actor import ThreatActor
from hexa_sec.domain.threat_intel.threat_intel import ThreatIntel


def _threat(
    actor_id: str = "APT-41",
    tactic: str = "initial_access",
    severity: Severity = Severity.CRITICAL,
    asset: str | None = "payment-api",
) -> Threat:
    assets = (AssetId(asset),) if asset else ()
    findings = (FindingId(f"cve-{actor_id}-{tactic}"),) if asset else ()
    return Threat(
        actor=ThreatActor(actor_id, f"{actor_id} group"),
        tactic=tactic,
        severity=severity,
        related_assets=assets,
        related_findings=findings,
    )


def test_for_asset_consolidates_threats() -> None:
    threats = (
        _threat(actor_id="APT-41", tactic="initial_access"),
        _threat(actor_id="FIN7", tactic="exfiltration", severity=Severity.HIGH),
    )
    risk = ThreatIntel.for_asset("payment-api", threats)
    assert risk.asset == "payment-api"
    assert len(risk.threats) == 2
    assert risk.threat_count == 2


def test_for_asset_deduplicates_same_actor_tactic() -> None:
    threats = (
        _threat(actor_id="APT-41", tactic="initial_access"),
        _threat(actor_id="APT-41", tactic="initial_access"),
    )
    risk = ThreatIntel.for_asset("payment-api", threats)
    assert len(risk.threats) == 1


def test_for_asset_dedup_keeps_higher_severity() -> None:
    threats = (
        _threat(actor_id="APT-41", tactic="initial_access", severity=Severity.MEDIUM),
        _threat(actor_id="APT-41", tactic="initial_access", severity=Severity.CRITICAL),
    )
    risk = ThreatIntel.for_asset("payment-api", threats)
    assert len(risk.threats) == 1
    assert risk.threats[0].severity is Severity.CRITICAL


def test_for_asset_keeps_only_touching_asset() -> None:
    threats = (_threat(asset="other-api"),)
    risk = ThreatIntel.for_asset("payment-api", threats)
    assert risk.threats == ()


def test_for_asset_matches_padded_asset_value() -> None:
    threat = _threat(asset="payment-api")
    padded = Threat(
        actor=ThreatActor("APT-41", "APT-41 group"),
        tactic="initial_access",
        severity=Severity.CRITICAL,
        related_assets=(AssetId("  payment-api  "),),
        related_findings=(FindingId("cve-APT-41-initial_access"),),
    )
    risk = ThreatIntel.for_asset("payment-api", (padded,))
    assert len(risk.threats) == 1


def test_for_asset_excludes_abstract_threat() -> None:
    threats = (_threat(asset=None),)
    risk = ThreatIntel.for_asset("payment-api", threats)
    assert risk.threats == ()


def test_for_asset_no_findings_returns_empty() -> None:
    risk = ThreatIntel.for_asset("payment-api", ())
    assert risk.threats == ()
    assert risk.threat_count == 0


def test_for_asset_rejects_blank_asset() -> None:
    with pytest.raises(ValueError):
        ThreatIntel.for_asset("   ", ())


def test_for_asset_is_deterministic() -> None:
    threats = (
        _threat(actor_id="APT-41", tactic="initial_access"),
        _threat(actor_id="FIN7", tactic="exfiltration", severity=Severity.HIGH),
    )
    first = ThreatIntel.for_asset("payment-api", threats)
    second = ThreatIntel.for_asset("payment-api", threats)
    assert first == second
    assert first.threat_count == second.threat_count


def test_for_asset_dedup_order_independent() -> None:
    medium = _threat(actor_id="APT-41", tactic="initial_access", severity=Severity.MEDIUM)
    high = _threat(actor_id="APT-41", tactic="initial_access", severity=Severity.HIGH)
    critical = _threat(actor_id="APT-41", tactic="initial_access", severity=Severity.CRITICAL)
    outcomes = {
        ThreatIntel.for_asset("payment-api", permutation).threats[0].severity
        for permutation in _permutations((medium, high, critical))
    }
    assert outcomes == {Severity.CRITICAL}


def _permutations(values: tuple[Threat, ...]) -> list[tuple[Threat, ...]]:
    if len(values) <= 1:
        return [values]
    out: list[tuple[Threat, ...]] = []
    for index in range(len(values)):
        rest = values[:index] + values[index + 1 :]
        for tail in _permutations(rest):
            out.append((values[index],) + tail)
    return out
