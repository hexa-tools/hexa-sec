"""Tests for BusinessAsset (context: business_impact, SEC-23)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.business_impact.business_asset import BusinessAsset
from hexa_sec.domain.business_impact.impact_level import ImpactLevel


def _asset(
    name: str = "billing",
    process: str = "invoicing",
    impact_level: ImpactLevel = ImpactLevel.HIGH,
) -> BusinessAsset:
    return BusinessAsset(name=name, process=process, impact_level=impact_level)


def test_business_asset_creation() -> None:
    asset = _asset()
    assert asset.name == "billing"
    assert asset.process == "invoicing"
    assert asset.impact_level is ImpactLevel.HIGH


def test_business_asset_normalizes_fields() -> None:
    asset = BusinessAsset("  billing  ", "  invoicing  ", ImpactLevel.HIGH)
    assert asset.name == "billing"
    assert asset.process == "invoicing"


def test_business_asset_rejects_empty_name() -> None:
    with pytest.raises(ValueError):
        _asset(name="")


def test_business_asset_rejects_blank_name() -> None:
    with pytest.raises(ValueError):
        _asset(name="   ")


def test_business_asset_rejects_empty_process() -> None:
    with pytest.raises(ValueError):
        _asset(process="")


def test_business_asset_rejects_blank_process() -> None:
    with pytest.raises(ValueError):
        _asset(process="   ")


def test_business_asset_rejects_non_impact_level() -> None:
    with pytest.raises(ValueError):
        BusinessAsset(name="billing", process="invoicing", impact_level="high")
