"""WifiFinding — a wireless network exposure or rogue access point (context: wifi_risk)."""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.wifi_risk.ssid import Bssid, Ssid
from hexa_sec.domain.wifi_risk.wifi_security import WifiSecurity


@dataclass(frozen=True)
class WifiFinding:
    """An observed wireless network and its risk posture."""

    ssid: Ssid
    security: WifiSecurity
    bssid: Bssid | None = None
    rogue: bool = False
    clients: int = 0

    def __post_init__(self) -> None:
        if self.clients < 0:
            raise ValueError("clients cannot be negative")

    def is_open(self) -> bool:
        return self.security is WifiSecurity.OPEN

    def is_rogue(self) -> bool:
        return self.rogue

    @property
    def weak(self) -> bool:
        return self.security.weak
