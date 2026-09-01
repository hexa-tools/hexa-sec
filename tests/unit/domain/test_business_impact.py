"""Tests for the BusinessImpact aggregate (context: business_impact, SEC-23)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.business_impact.business_asset import BusinessAsset
from hexa_sec.domain.business_impact.business_impact import BusinessImpact
from hexa_sec.domain.business_impact.impact_level import ImpactLevel


def _asset(
    name: str = "billing",
    process: str = "invoicing",
    impact_level: ImpactLevel = ImpactLevel.HIGH,
) -> BusinessAsset:
    return BusinessAsset(name=name, process=process, impact_level=impact_level)


def test_for_asset_consolidates_assets() -> None:
    assets = (
        _asset(process="invoicing", impact_level=ImpactLevel.CRITICAL),
        _asset(process="payments", impact_level=ImpactLevel.MEDIUM),
    )
    impact = BusinessImpact.for_asset("billing", assets)
    assert impact.name == "billing"
    assert len(impact.assets) == 2
    assert impact.critical_count == 1


def test_for_asset_deduplicates_same_name_process() -> None:
    assets = (_asset(), _asset())
    impact = BusinessImpact.for_asset("billing", assets)
    assert len(impact.assets) == 1


def test_for_asset_keeps_distinct_processes() -> None:
    assets = (
        _asset(process="invoicing"),
        _asset(process="payments"),
    )
    impact = BusinessImpact.for_asset("billing", assets)
    assert len(impact.assets) == 2


def test_for_asset_only_matching_name() -> None:
    impact = BusinessImpact.for_asset("billing", (_asset(name="crm"),))
    assert impact.assets == ()
    assert impact.critical_count == 0


def test_for_asset_no_assets_returns_empty() -> None:
    impact = BusinessImpact.for_asset("billing", ())
    assert impact.assets == ()
    assert impact.critical_count == 0


def test_for_asset_critical_assets() -> None:
    assets = (
        _asset(process="invoicing", impact_level=ImpactLevel.CRITICAL),
        _asset(process="payments", impact_level=ImpactLevel.LOW),
    )
    impact = BusinessImpact.for_asset("billing", assets)
    assert [a.process for a in impact.critical_assets()] == ["invoicing"]
    assert impact.critical_count == 1


def test_for_asset_is_deterministic() -> None:
    assets = (
        _asset(process="invoicing", impact_level=ImpactLevel.CRITICAL),
        _asset(process="payments", impact_level=ImpactLevel.MEDIUM),
    )
    first = BusinessImpact.for_asset("billing", assets)
    second = BusinessImpact.for_asset("billing", assets)
    assert first == second
    assert first.critical_count == second.critical_count


def test_for_asset_rejects_blank_name() -> None:
    with pytest.raises(ValueError):
        BusinessImpact.for_asset("   ", ())


# --- Category: concurrence / ordre (dedup impact_level le plus élevé) -------


def test_for_asset_dedup_keeps_highest_impact() -> None:
    high = _asset(process="invoicing", impact_level=ImpactLevel.HIGH)
    critical = _asset(process="invoicing", impact_level=ImpactLevel.CRITICAL)
    impact = BusinessImpact.for_asset("billing", (high, critical))
    assert len(impact.assets) == 1
    assert impact.assets[0].impact_level is ImpactLevel.CRITICAL


def test_for_asset_dedup_order_independent_for_impact() -> None:
    high = _asset(process="invoicing", impact_level=ImpactLevel.HIGH)
    critical = _asset(process="invoicing", impact_level=ImpactLevel.CRITICAL)
    first = BusinessImpact.for_asset("billing", (high, critical))
    second = BusinessImpact.for_asset("billing", (critical, high))
    assert first == second
    assert first.assets[0].impact_level is ImpactLevel.CRITICAL
