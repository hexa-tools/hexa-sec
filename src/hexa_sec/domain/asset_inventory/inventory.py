"""InventoryEntry + AssetInventory — the infrastructure inventory (context: asset_inventory).

The inventory is what the scanners discovered: open ports, the application on
each, and the detected version. An ``AssetInventory`` consolidates the entries
of a single asset.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.asset_inventory.port import Application, Port, Version


@dataclass(frozen=True)
class InventoryEntry:
    """A single discovered port on an asset."""

    host: str
    port: Port
    application: Application
    version: Version | None = None

    def __post_init__(self) -> None:
        if not self.host.strip():
            raise ValueError("inventory host cannot be empty")


@dataclass(frozen=True)
class AssetInventory:
    """The consolidated inventory of one asset (host -> ports)."""

    host: str
    entries: tuple[InventoryEntry, ...] = ()

    def __post_init__(self) -> None:
        if not self.host.strip():
            raise ValueError("inventory host cannot be empty")
        for entry in self.entries:
            if entry.host != self.host:
                raise ValueError("entry host must match the inventory host")
        seen: set[tuple[int, str]] = set()
        for entry in self.entries:
            key = (entry.port.number, entry.application.name)
            if key in seen:
                raise ValueError(f"duplicate port/application in inventory: {key}")
            seen.add(key)

    def open_ports(self) -> tuple[Port, ...]:
        return tuple(entry.port for entry in self.entries)

    def applications(self) -> tuple[Application, ...]:
        return tuple(entry.application for entry in self.entries)

    def version_of(self, name: str) -> Version | None:
        normalized = name.strip().lower()
        for entry in self.entries:
            if entry.application.name == normalized:
                return entry.version
        return None

    def count(self) -> int:
        return len(self.entries)

    def with_entry(self, entry: InventoryEntry) -> AssetInventory:
        return AssetInventory(host=self.host, entries=(*self.entries, entry))
