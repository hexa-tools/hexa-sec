"""ScanAssetService — scans an asset after the mandate check (US-1, scaffold).

Phase 2 wires the scanner ports + the mandate port. Never try/catch here —
let HexaSecError propagate.
"""

from __future__ import annotations

from hexa_sec.application.ports.driven.secret_store_port import SecretStorePort
from hexa_sec.application.ports.driven.web_scanner_port import WebScannerPort
from hexa_sec.application.ports.driving.scan_asset.scan_asset_service_port import (
    ScanAssetCommand,
    ScanAssetResult,
    ScanAssetServicePort,
)


class ScanAssetService(ScanAssetServicePort):
    """Orchestrate scanners on an asset (bootstrap stub)."""

    def __init__(
        self,
        web_scanner: WebScannerPort | None = None,
        network_scanner: object | None = None,
        secret_store: SecretStorePort | None = None,
    ) -> None:
        self._web_scanner = web_scanner
        self._network_scanner = network_scanner
        self._secret_store = secret_store

    def scan(self, command: ScanAssetCommand) -> ScanAssetResult:
        raise NotImplementedError  # pragma: no cover
