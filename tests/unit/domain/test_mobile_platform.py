"""Tests for MobilePlatform (context: mobile_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.mobile_risk.mobile_platform import MobilePlatform


def test_mobile_platform_values() -> None:
    assert MobilePlatform.ANDROID.value == "android"
    assert MobilePlatform.IOS.value == "ios"


def test_mobile_platform_is_unique() -> None:
    values = [member.value for member in MobilePlatform]
    assert len(values) == len(set(values))


def test_mobile_platform_normalize_accepts_known() -> None:
    assert MobilePlatform.normalize("android") is MobilePlatform.ANDROID
    assert MobilePlatform.normalize("IOS") is MobilePlatform.IOS


def test_mobile_platform_normalize_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="unknown mobile platform: windows"):
        MobilePlatform.normalize("windows")


def test_mobile_platform_normalize_rejects_blank() -> None:
    with pytest.raises(ValueError, match="unknown mobile platform:"):
        MobilePlatform.normalize("   ")
