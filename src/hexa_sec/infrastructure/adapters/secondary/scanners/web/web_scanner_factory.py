"""Web scanner factory — one adapter per vendor (Factory pattern)."""

from __future__ import annotations

from hexa_sec.application.ports.driven.web_scanner_port import WebFindingRecord, WebScannerPort
from hexa_sec.domain.errors import ScannerUnavailableError

KNOWN_VENDORS = frozenset({"burp", "zap", "nuclei", "wpscan", "nikto"})


class WebScannerAdapter(WebScannerPort):
    """Bootstrap stub — Phase 3 swaps in the real per-vendor adapter."""

    def __init__(self, vendor: str) -> None:
        self.vendor = vendor

    def scan(self, asset: str) -> list[WebFindingRecord]:
        raise NotImplementedError  # pragma: no cover


def create_web_scanner(vendor: str) -> WebScannerPort:
    """Return the adapter for ``vendor``, or raise a Scanner error."""
    if vendor not in KNOWN_VENDORS:
        raise ScannerUnavailableError(f"unknown web scanner vendor: {vendor}")
    return WebScannerAdapter(vendor)
