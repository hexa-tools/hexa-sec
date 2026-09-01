"""Tests for ScanAssetService (US-1 orchestration stub)."""

from __future__ import annotations

import pytest

from hexa_sec.application.ports.driving.scan_asset.scan_asset_service_port import ScanAssetCommand
from hexa_sec.application.service.scan_asset_service import ScanAssetService


def test_scan_asset_service_is_not_implemented() -> None:
    service = ScanAssetService()
    command: ScanAssetCommand = {"asset": "10.0.0.1", "mandate_id": "mnd_0001", "vendor": "nessus"}
    with pytest.raises(NotImplementedError):
        service.scan(command)
