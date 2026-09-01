"""ScanAssetUseCase — application entry for launching a scan (US-1)."""

from __future__ import annotations

from hexa_sec.application.ports.driving.scan_asset.scan_asset_service_port import (
    ScanAssetCommand,
    ScanAssetResult,
    ScanAssetServicePort,
)


class ScanAssetUseCase(ScanAssetServicePort):
    """Depends on the service ABC so it is mockable per test."""

    def __init__(self, service: ScanAssetServicePort) -> None:
        self._service = service

    def scan(self, command: ScanAssetCommand) -> ScanAssetResult:
        return self._service.scan(command)
