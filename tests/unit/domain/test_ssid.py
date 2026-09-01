"""Tests for Ssid + Bssid (context: wifi_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.wifi_risk.ssid import Bssid, Ssid


def test_ssid_value() -> None:
    assert Ssid("Office-WiFi").value == "Office-WiFi"


def test_ssid_trims_whitespace() -> None:
    assert Ssid("  Guest  ").value == "Guest"


def test_ssid_rejects_empty() -> None:
    with pytest.raises(ValueError):
        Ssid("   ")


def test_ssid_rejects_too_long() -> None:
    with pytest.raises(ValueError):
        Ssid("x" * 33)


def test_bssid_value() -> None:
    assert Bssid("AA:BB:CC:DD:EE:FF").value == "AA:BB:CC:DD:EE:FF"


def test_bssid_rejects_empty() -> None:
    with pytest.raises(ValueError):
        Bssid("")


def test_bssid_normalizes_value() -> None:
    assert Bssid("  AA:BB:CC:DD:EE:FF  ").value == "AA:BB:CC:DD:EE:FF"
