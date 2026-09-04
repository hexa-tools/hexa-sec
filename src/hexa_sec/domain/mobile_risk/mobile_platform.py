"""MobilePlatform — the mobile OS audited (context: mobile_risk)."""

from __future__ import annotations

from enum import Enum


class MobilePlatform(Enum):
    """A supported mobile application platform."""

    ANDROID = "android"
    IOS = "ios"

    @classmethod
    def normalize(cls, raw: str) -> MobilePlatform:
        """Map a raw label to a ``MobilePlatform``; unknown values are rejected."""
        cleaned = raw.strip().lower()
        try:
            return cls(cleaned)
        except ValueError as error:
            raise ValueError(f"unknown mobile platform: {raw}") from error
