"""Tests for ScanAssetUseCase (US-1)."""

from __future__ import annotations

import pytest

from hexa_sec.application.ports.driving.scan_asset.scan_asset_service_port import ScanAssetCommand
from hexa_sec.application.service.scan_asset_service import ScanAssetService
from hexa_sec.application.use_case.scan_asset.scan_asset_use_case import ScanAssetUseCase


def test_scan_asset_use_case_delegates_to_service() -> None:
    use_case = ScanAssetUseCase(ScanAssetService())
    command: ScanAssetCommand = {"asset": "10.0.0.1", "mandate_id": "mnd_0001", "vendor": "nessus"}
    with pytest.raises(NotImplementedError):
        use_case.scan(command)
