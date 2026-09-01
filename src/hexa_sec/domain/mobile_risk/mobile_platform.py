"""MobilePlatform — the mobile OS audited (context: mobile_risk)."""

from __future__ import annotations

from enum import Enum


class MobilePlatform(Enum):
    """A supported mobile application platform."""

    ANDROID = "android"
    IOS = "ios"
