"""Tests for AssetId + Asset (context: asset)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.asset.asset import Asset, AssetId
from hexa_sec.domain.asset.asset_criticality import AssetCriticality
from hexa_sec.domain.asset.asset_type import AssetType


def test_asset_id_defaults_none() -> None:
    asset = Asset(name="api-gateway", type=AssetType.HOST)
    assert asset.asset_id is None
    assert asset.name == "api-gateway"
    assert asset.type is AssetType.HOST
    assert asset.criticality is AssetCriticality.PUBLIC


def test_asset_id_explicit() -> None:
    asset_id = AssetId("ast_0001")
    asset = Asset(asset_id=asset_id, name="crm", type=AssetType.WEB_APP)
    assert asset.asset_id == asset_id


def test_asset_rejects_empty_name() -> None:
    with pytest.raises(ValueError):
        Asset(name="", type=AssetType.HOST)
    with pytest.raises(ValueError):
        Asset(name="   ", type=AssetType.WEB_APP)


def test_asset_is_web_predicate() -> None:
    assert Asset(name="site", type=AssetType.WEB_APP).is_web() is True
    assert Asset(name="host", type=AssetType.HOST).is_web() is False


def test_asset_is_exposed_predicate() -> None:
    assert Asset(name="site", type=AssetType.WEB_APP).is_exposed() is True
    assert Asset(name="host", type=AssetType.HOST).is_exposed() is True
    assert Asset(name="repo", type=AssetType.REPO).is_exposed() is False


def test_asset_equality_by_value() -> None:
    first = Asset(name="db", type=AssetType.HOST)
    second = Asset(name="db", type=AssetType.HOST)
    assert first == second
