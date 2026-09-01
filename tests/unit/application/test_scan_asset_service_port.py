"""Tests for ScanAssetServicePort (driving port — US-1)."""

from __future__ import annotations

import inspect

from hexa_sec.application.ports.driving.scan_asset.scan_asset_service_port import ScanAssetServicePort


def test_scan_asset_service_port_is_abstract() -> None:
    assert inspect.isabstract(ScanAssetServicePort) is True
