"""Ssid + Bssid — a wireless network identity (context: wifi_risk)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Ssid:
    """The service set identifier of a wireless network."""

    value: str

    def __post_init__(self) -> None:
        name = self.value.strip()
        if not name:
            raise ValueError("ssid cannot be empty")
        if len(name) > 32:
            raise ValueError("ssid cannot exceed 32 characters")
        object.__setattr__(self, "value", name)


@dataclass(frozen=True)
class Bssid:
    """The MAC address of an access point."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("bssid cannot be empty")
