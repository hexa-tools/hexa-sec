"""Tests for AssetType (context: asset)."""

from __future__ import annotations

from hexa_sec.domain.asset.asset_type import AssetType


def test_asset_type_has_core_members() -> None:
    assert AssetType.HOST.value == "host"
    assert AssetType.WEB_APP.value == "web_app"
    assert AssetType.REPO.value == "repo"
    assert AssetType.CLOUD.value == "cloud"


def test_asset_type_is_unique() -> None:
    values = [member.value for member in AssetType]
    assert len(values) == len(set(values))


def test_asset_type_roundtrip_by_value() -> None:
    assert AssetType(AssetType.HOST.value) is AssetType.HOST
