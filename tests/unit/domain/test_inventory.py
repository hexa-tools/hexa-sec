"""Tests for InventoryEntry + AssetInventory (context: asset_inventory, SEC-5)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.asset_inventory.inventory import AssetInventory, InventoryEntry
from hexa_sec.domain.asset_inventory.port import Application, Port, Version


def _entry(
    host: str = "10.0.0.1", port: int = 443, app: str = "https", version: str | None = "1.24"
) -> InventoryEntry:
    return InventoryEntry(
        host=host,
        port=Port(port),
        application=Application(app),
        version=Version(version) if version else None,
    )


def test_inventory_entry_creation() -> None:
    entry = _entry()
    assert entry.host == "10.0.0.1"
    assert entry.port.number == 443
    assert entry.application.name == "https"
    assert entry.version is not None
    assert entry.version.value == "1.24"


def test_inventory_entry_default_version_none() -> None:
    entry = _entry(version=None)
    assert entry.version is None


def test_inventory_entry_rejects_empty_host() -> None:
    with pytest.raises(ValueError):
        _entry(host="")


def test_asset_inventory_creation() -> None:
    inventory = AssetInventory(
        host="10.0.0.1", entries=(_entry(port=443), _entry(port=22, app="ssh"))
    )
    assert inventory.count() == 2
    assert inventory.host == "10.0.0.1"


def test_asset_inventory_open_ports() -> None:
    inventory = AssetInventory(
        host="10.0.0.1", entries=(_entry(port=443), _entry(port=22, app="ssh"))
    )
    assert inventory.open_ports() == (Port(443), Port(22))


def test_asset_inventory_applications() -> None:
    inventory = AssetInventory(
        host="10.0.0.1", entries=(_entry(port=443), _entry(port=22, app="ssh"))
    )
    assert inventory.applications() == (Application("https"), Application("ssh"))


def test_asset_inventory_version_of() -> None:
    inventory = AssetInventory(
        host="10.0.0.1", entries=(_entry(port=22, app="ssh", version="9.6p1"),)
    )
    assert inventory.version_of("ssh") is not None
    assert inventory.version_of("ssh").value == "9.6p1"
    assert inventory.version_of("ftp") is None


def test_asset_inventory_rejects_entry_host_mismatch() -> None:
    with pytest.raises(ValueError):
        AssetInventory(host="10.0.0.1", entries=(_entry(host="10.0.0.2"),))


def test_asset_inventory_rejects_duplicate_port_and_application() -> None:
    with pytest.raises(ValueError):
        AssetInventory(host="10.0.0.1", entries=(_entry(port=443), _entry(port=443)))


def test_asset_inventory_rejects_empty_host() -> None:
    with pytest.raises(ValueError):
        AssetInventory(host="", entries=(_entry(),))


def test_asset_inventory_with_entry_is_immutable() -> None:
    inventory = AssetInventory(host="10.0.0.1", entries=(_entry(port=443),))
    extended = inventory.with_entry(_entry(port=22, app="ssh"))
    assert inventory.count() == 1
    assert extended.count() == 2


def test_empty_inventory_is_a_distinct_valid_state() -> None:
    # catégorie « absence/vide » : un asset sans port ouvert est un état
    # mesuré distinct (pas un succès silencieux) — représenté par un
    # inventaire vide, jamais confondu avec "non scanné".
    inventory = AssetInventory(host="10.0.0.1")
    assert inventory.count() == 0
    assert inventory.open_ports() == ()


def test_asset_inventory_version_of_is_case_insensitive() -> None:
    # catégorie « invariant de cohérence » : version_of doit se comporter
    # comme Application (normalisation lowercase) — "SSH" trouve "ssh".
    inventory = AssetInventory(
        host="10.0.0.1", entries=(_entry(port=22, app="ssh", version="9.6p1"),)
    )
    assert inventory.version_of("SSH").value == "9.6p1"
    assert inventory.version_of("  ssh ").value == "9.6p1"


# --- Catégorie: consolidation par asset (for_asset) + normalisation + validation ---


def test_for_asset_consolidates_entries() -> None:
    entries = (_entry(port=443), _entry(port=22, app="ssh"), _entry(port=80, app="http"))
    inventory = AssetInventory.for_asset("10.0.0.1", entries)
    assert inventory.host == "10.0.0.1"
    assert inventory.count() == 3


def test_for_asset_deduplicates_same_port() -> None:
    entries = (_entry(port=443), _entry(port=443))
    inventory = AssetInventory.for_asset("10.0.0.1", entries)
    assert inventory.count() == 1


def test_for_asset_ignores_other_host() -> None:
    entries = (_entry(port=443), _entry(port=22, app="ssh", host="10.0.0.2"))
    inventory = AssetInventory.for_asset("10.0.0.1", entries)
    assert inventory.count() == 1


def test_for_asset_normalizes_host() -> None:
    inventory = AssetInventory.for_asset("  10.0.0.1  ", (_entry(port=443),))
    assert inventory.host == "10.0.0.1"
    assert inventory.count() == 1


def test_asset_inventory_normalizes_host() -> None:
    inventory = AssetInventory(host="  10.0.0.1  ", entries=(_entry(port=443),))
    assert inventory.host == "10.0.0.1"


def test_inventory_entry_normalizes_host() -> None:
    entry = _entry(host="  10.0.0.1  ")
    assert entry.host == "10.0.0.1"


def test_inventory_entry_rejects_non_port() -> None:
    with pytest.raises(ValueError):
        InventoryEntry(host="10.0.0.1", port=443, application=Application("http"))  # type: ignore[arg-type]


def test_inventory_entry_rejects_non_application() -> None:
    with pytest.raises(ValueError):
        InventoryEntry(host="10.0.0.1", port=Port(443), application="http")  # type: ignore[arg-type]


def test_for_asset_rejects_empty_host() -> None:
    with pytest.raises(ValueError):
        AssetInventory.for_asset("   ", (_entry(port=443),))
