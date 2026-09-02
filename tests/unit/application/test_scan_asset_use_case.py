"""Tests for ScanAssetUseCase (US-1)."""

from __future__ import annotations

from hexa_sec.application.ports.driving.scan_asset.scan_asset_service_port import (
    ScanAssetCommand,
    ScanAssetResult,
    ScanAssetServicePort,
)
from hexa_sec.application.use_case.scan_asset.scan_asset_use_case import ScanAssetUseCase


class _StubService(ScanAssetServicePort):
    def scan(self, command: ScanAssetCommand) -> ScanAssetResult:
        return {"scan_id": "scan_0001", "status": "pending", "mandate_id": "mnd_0001", "findings": []}


def test_scan_asset_use_case_delegates_to_service() -> None:
    use_case = ScanAssetUseCase(_StubService())
    command: ScanAssetCommand = {
        "asset": "10.0.0.1",
        "mandate_id": "mnd_0001",
        "vendor": "nessus",
        "tenant_id": "tnt_0001",
        "depth": "complete",
        "exclusions": (),
    }
    result = use_case.scan(command)
    assert result["scan_id"] == "scan_0001"
    assert result["status"] == "pending"
