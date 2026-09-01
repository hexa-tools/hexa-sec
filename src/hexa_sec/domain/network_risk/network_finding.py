"""NetworkFinding — an exposed port/service (context: network_risk, SEC-11).

An adapter (nmap/masscan/...) translates a scanner result into a NetworkFinding:
the asset, the anonymous ``Port``, the detected ``application`` (the port's
service), its ``Banner`` and its Internet ``Exposure``. The value objects
``Port`` and ``Application`` come from ``asset_inventory`` (context 5, DRY).
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.asset_inventory.port import Application, Port
from hexa_sec.domain.network_risk.banner import Banner
from hexa_sec.domain.network_risk.exposure import Exposure


@dataclass(frozen=True)
class NetworkFinding:
    """A single network-level exposure on an asset."""

    asset: str
    port: Port
    service: Application
    banner: Banner
    exposure: Exposure

    def __post_init__(self) -> None:
        if not self.asset or not self.asset.strip():
            raise ValueError("network finding asset cannot be empty")
        if not isinstance(self.exposure, Exposure):
            raise ValueError("network finding exposure must be an Exposure")
