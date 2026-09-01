"""Tests for WifiFinding (context: wifi_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.wifi_risk.ssid import Bssid, Ssid
from hexa_sec.domain.wifi_risk.wifi_finding import WifiFinding
from hexa_sec.domain.wifi_risk.wifi_security import WifiSecurity


def test_wifi_finding_creation() -> None:
    finding = WifiFinding(ssid=Ssid("Office"), security=WifiSecurity.WPA2, clients=12)
    assert finding.ssid.value == "Office"
    assert finding.security is WifiSecurity.WPA2
    assert finding.clients == 12
    assert finding.rogue is False
    assert finding.bssid is None


def test_wifi_finding_is_open() -> None:
    finding = WifiFinding(ssid=Ssid("Free"), security=WifiSecurity.OPEN)
    assert finding.is_open() is True


def test_wifi_finding_weak() -> None:
    assert WifiFinding(ssid=Ssid("x"), security=WifiSecurity.WPA).weak is True
    assert WifiFinding(ssid=Ssid("x"), security=WifiSecurity.WPA3).weak is False


def test_wifi_finding_rogue() -> None:
    finding = WifiFinding(ssid=Ssid("EvilTwin"), security=WifiSecurity.WPA2, rogue=True)
    assert finding.is_rogue() is True


def test_wifi_finding_rejects_negative_clients() -> None:
    with pytest.raises(ValueError):
        WifiFinding(ssid=Ssid("x"), security=WifiSecurity.WPA2, clients=-1)


def test_wifi_finding_with_bssid() -> None:
    finding = WifiFinding(
        ssid=Ssid("Office"), security=WifiSecurity.WPA3, bssid=Bssid("AA:BB:CC:DD:EE:FF")
    )
    assert finding.bssid is not None


def test_wifi_finding_rejects_non_ssid() -> None:
    with pytest.raises(ValueError):
        WifiFinding(ssid="Office", security=WifiSecurity.WPA2)  # type: ignore[arg-type]


def test_wifi_finding_rejects_non_security() -> None:
    with pytest.raises(ValueError):
        WifiFinding(ssid=Ssid("Office"), security="wpa2")  # type: ignore[arg-type]


def test_wifi_finding_rejects_non_bssid() -> None:
    with pytest.raises(ValueError):
        WifiFinding(ssid=Ssid("Office"), security=WifiSecurity.WPA2, bssid="AA:BB:CC:DD:EE:FF")  # type: ignore[arg-type]
