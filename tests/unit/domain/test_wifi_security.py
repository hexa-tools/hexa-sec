"""Tests for WifiSecurity (context: wifi_risk)."""

from __future__ import annotations

from hexa_sec.domain.wifi_risk.wifi_security import WifiSecurity


def test_wifi_security_values() -> None:
    assert WifiSecurity.OPEN.value == "open"
    assert WifiSecurity.WPA3.value == "wpa3"


def test_wifi_security_is_unique() -> None:
    values = [member.value for member in WifiSecurity]
    assert len(values) == len(set(values))


def test_wifi_security_weak() -> None:
    assert WifiSecurity.OPEN.weak is True
    assert WifiSecurity.WEP.weak is True
    assert WifiSecurity.WPA.weak is True
    assert WifiSecurity.WPA2.weak is False
    assert WifiSecurity.WPA3.weak is False
