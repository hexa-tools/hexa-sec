"""Tests for VendorConfig (context: pack_config)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.pack_config.vendor_config import VendorConfig


def test_vendor_config_creation() -> None:
    config = VendorConfig(provider="shodan", keys=("SHODAN_API_KEY", "SHODAN_SECRET"))
    assert config.provider == "shodan"
    assert config.keys == ("SHODAN_API_KEY", "SHODAN_SECRET")


def test_vendor_config_normalizes_fields() -> None:
    config = VendorConfig(provider="  shodan  ", keys=("  SHODAN_API_KEY  ",))
    assert config.provider == "shodan"
    assert config.keys == ("SHODAN_API_KEY",)


def test_vendor_config_rejects_empty_provider() -> None:
    with pytest.raises(ValueError):
        VendorConfig(provider="", keys=("KEY",))


def test_vendor_config_rejects_empty_key() -> None:
    with pytest.raises(ValueError):
        VendorConfig(provider="shodan", keys=("",))


def test_vendor_config_rejects_value_like_key() -> None:
    with pytest.raises(ValueError):
        VendorConfig(provider="shodan", keys=("SHODAN_API_KEY=abc123",))


def test_vendor_config_rejects_secret_key() -> None:
    with pytest.raises(ValueError):
        VendorConfig(provider="openai", keys=("sk-abc123",))
