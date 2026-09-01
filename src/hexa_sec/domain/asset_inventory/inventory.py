"""InventoryEntry — a discovered host/port/service (context: asset_inventory)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InventoryEntry:
    """A single discovered element of the infrastructure inventory."""

    host: str
    port: int
    service: str

    def __post_init__(self) -> None:
        if not self.host:
            raise ValueError("inventory host cannot be empty")
        if not 0 < self.port < 65536:
            raise ValueError("inventory port must be between 1 and 65535")
