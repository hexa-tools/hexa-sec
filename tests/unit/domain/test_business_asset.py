"""Tests for BusinessAsset (context: business_impact)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.business_impact.business_asset import BusinessAsset


def test_business_asset_creation() -> None:
    asset = BusinessAsset(name="billing", process="invoicing")
    assert asset.process == "invoicing"


def test_business_asset_rejects_empty_process() -> None:
    with pytest.raises(ValueError):
        BusinessAsset(name="billing", process="")


def test_business_asset_rejects_empty_name() -> None:
    with pytest.raises(ValueError):
        BusinessAsset(name="", process="invoicing")
