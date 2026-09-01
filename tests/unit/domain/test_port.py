"""Tests for Port / Application / Version value objects (context: asset_inventory)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.asset_inventory.port import Application, Port, Version


def test_port_creation() -> None:
    assert Port(443).number == 443
    assert Port(1).number == 1
    assert Port(65535).number == 65535


def test_port_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        Port(0)
    with pytest.raises(ValueError):
        Port(65536)
    with pytest.raises(ValueError):
        Port(-1)


def test_application_normalizes_name() -> None:
    assert Application("HTTPS").name == "https"
    assert Application("ssh").name == "ssh"


def test_application_rejects_empty() -> None:
    with pytest.raises(ValueError):
        Application("")
    with pytest.raises(ValueError):
        Application("   ")


def test_version_trims_value() -> None:
    assert Version("  9.6p1 ").value == "9.6p1"


def test_version_rejects_empty() -> None:
    with pytest.raises(ValueError):
        Version("")
    with pytest.raises(ValueError):
        Version("   ")
