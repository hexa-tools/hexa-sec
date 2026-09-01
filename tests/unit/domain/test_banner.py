"""Tests for the Banner value object (context: network_risk, SEC-11)."""

from __future__ import annotations

from hexa_sec.domain.network_risk.banner import Banner


def test_banner_trims_and_is_present() -> None:
    banner = Banner("  SSH-2.0-OpenSSH  ")
    assert banner.text == "SSH-2.0-OpenSSH"
    assert banner.is_present is True


def test_banner_null_safe_without_inventing() -> None:
    absent = Banner("")
    assert absent.text == ""
    assert absent.is_present is False
