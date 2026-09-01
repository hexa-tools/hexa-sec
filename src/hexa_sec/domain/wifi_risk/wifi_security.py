"""WifiSecurity — the encryption/security mode of an access point (context: wifi_risk)."""

from __future__ import annotations

from enum import Enum


class WifiSecurity(Enum):
    """Wireless security mode detected on an access point."""

    OPEN = "open"
    WEP = "wep"
    WPA = "wpa"
    WPA2 = "wpa2"
    WPA3 = "wpa3"

    @property
    def weak(self) -> bool:
        return self in (WifiSecurity.OPEN, WifiSecurity.WEP, WifiSecurity.WPA)
