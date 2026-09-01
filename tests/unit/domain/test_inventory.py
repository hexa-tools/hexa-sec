"""Tests for InventoryEntry (context: asset_inventory)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.asset_inventory.inventory import InventoryEntry


def test_inventory_entry_creation() -> None:
    entry = InventoryEntry(host="10.0.0.1", port=443, service="https")
    assert entry.service == "https"


def test_inventory_entry_rejects_empty_host() -> None:
    with pytest.raises(ValueError):
        InventoryEntry(host="", port=443, service="https")


def test_inventory_entry_rejects_invalid_port() -> None:
    with pytest.raises(ValueError):
        InventoryEntry(host="10.0.0.1", port=70000, service="https")
