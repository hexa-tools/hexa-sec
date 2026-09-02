"""Tests for the WifiRisk aggregate (context: wifi_risk)."""

from __future__ import annotations

from hexa_sec.domain.wifi_risk.ssid import Bssid, Ssid
from hexa_sec.domain.wifi_risk.wifi_finding import WifiFinding
from hexa_sec.domain.wifi_risk.wifi_risk import WifiRisk
from hexa_sec.domain.wifi_risk.wifi_security import WifiSecurity


def _finding(
    ssid: str,
    security: WifiSecurity,
    bssid: str | None = None,
    rogue: bool = False,
) -> WifiFinding:
    return WifiFinding(
        ssid=Ssid(ssid),
        security=security,
        bssid=Bssid(bssid) if bssid else None,
        rogue=rogue,
        clients=3,
    )


def test_of_consolidates_findings() -> None:
    findings = (
        _finding("Office", WifiSecurity.WPA2, "AA:BB:CC:DD:EE:01"),
        _finding("Free", WifiSecurity.OPEN, "AA:BB:CC:DD:EE:02"),
    )
    risk = WifiRisk.of(findings)
    assert len(risk.findings) == 2
    assert risk.weak_count == 1
    assert risk.rogue_count == 0


def test_of_deduplicates_same_ssid_bssid() -> None:
    findings = (
        _finding("Office", WifiSecurity.WPA2, "AA:BB:CC:DD:EE:01"),
        _finding("Office", WifiSecurity.WPA2, "AA:BB:CC:DD:EE:01"),
    )
    risk = WifiRisk.of(findings)
    assert len(risk.findings) == 1


def test_of_keeps_rogue() -> None:
    findings = (
        _finding("Office", WifiSecurity.WPA2, "AA:BB:CC:DD:EE:01", rogue=False),
        _finding("Office", WifiSecurity.WPA2, "AA:BB:CC:DD:EE:01", rogue=True),
    )
    risk = WifiRisk.of(findings)
    assert len(risk.findings) == 1
    assert risk.findings[0].is_rogue() is True


# --- Category: stabilité / déterminisme (ordre total sur clients) ----------
def test_of_dedup_is_order_independent_for_clients() -> None:
    finding_5 = WifiFinding(
        Ssid("Office"), WifiSecurity.WPA2, Bssid("AA:BB:CC:DD:EE:FF"), rogue=True, clients=5
    )
    finding_12 = WifiFinding(
        Ssid("Office"), WifiSecurity.WPA2, Bssid("AA:BB:CC:DD:EE:FF"), rogue=True, clients=12
    )
    first = WifiRisk.of((finding_5, finding_12))
    second = WifiRisk.of((finding_12, finding_5))
    assert first == second
    assert first.findings[0].clients == 12


def test_of_weak_networks() -> None:
    findings = (
        _finding("Free", WifiSecurity.OPEN, "AA:BB:CC:DD:EE:01"),
        _finding("Office", WifiSecurity.WPA3, "AA:BB:CC:DD:EE:02"),
    )
    risk = WifiRisk.of(findings)
    assert risk.weak_networks() == ("Free",)
    assert risk.weak_count == 1


def test_of_empty_is_empty() -> None:
    risk = WifiRisk.of(())
    assert risk.findings == ()
    assert risk.weak_count == 0
    assert risk.rogue_count == 0


def test_of_is_deterministic() -> None:
    findings = (
        _finding("Free", WifiSecurity.OPEN, "AA:BB:CC:DD:EE:01"),
        _finding("Office", WifiSecurity.WPA3, "AA:BB:CC:DD:EE:02"),
    )
    first = WifiRisk.of(findings)
    second = WifiRisk.of(findings)
    assert first == second
    assert first.weak_count == second.weak_count


def test_of_order_independent() -> None:
    a = _finding("Free", WifiSecurity.OPEN, "AA:BB:CC:DD:EE:01")
    b = _finding("Office", WifiSecurity.WPA3, "AA:BB:CC:DD:EE:02")
    first = WifiRisk.of((a, b))
    second = WifiRisk.of((b, a))
    assert first == second
    assert [finding.ssid.value for finding in first.findings] == [
        finding.ssid.value for finding in second.findings
    ]
