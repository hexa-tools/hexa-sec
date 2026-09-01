"""Tests for MobilePlatform (context: mobile_risk)."""

from __future__ import annotations

from hexa_sec.domain.mobile_risk.mobile_platform import MobilePlatform


def test_mobile_platform_values() -> None:
    assert MobilePlatform.ANDROID.value == "android"
    assert MobilePlatform.IOS.value == "ios"


def test_mobile_platform_is_unique() -> None:
    values = [member.value for member in MobilePlatform]
    assert len(values) == len(set(values))
