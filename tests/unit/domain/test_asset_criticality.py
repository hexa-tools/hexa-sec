"""Tests for AssetCriticality (context: asset)."""

from __future__ import annotations

from hexa_sec.domain.asset.asset_criticality import AssetCriticality


def test_asset_criticality_members() -> None:
    assert AssetCriticality.ERP.value == "erp"
    assert AssetCriticality.CRM.value == "crm"
    assert AssetCriticality.PUBLIC.value == "public"


def test_asset_criticality_is_unique() -> None:
    values = [member.value for member in AssetCriticality]
    assert len(values) == len(set(values))


def test_asset_criticality_order_max_to_min() -> None:
    assert AssetCriticality.ERP.weight > AssetCriticality.PUBLIC.weight
