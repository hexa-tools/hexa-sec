"""Tests for the scanner adapter factory/registry."""

from __future__ import annotations

import pytest

from hexa_sec.infrastructure.adapters.secondary.scanners.scanner_factory import create_scanner_adapter
from hexa_sec.infrastructure.adapters.secondary.scanners.network.nmap_adapter import NmapAdapter
from hexa_sec.infrastructure.adapters.secondary.scanners.web.burp_adapter import BurpAdapter
from hexa_sec.infrastructure.adapters.secondary.scanners.web.nuclei_adapter import NucleiAdapter
from hexa_sec.infrastructure.adapters.secondary.scanners.web.zap_adapter import ZapAdapter
from hexa_sec.application.ports.driven.network_scanner_port import NetworkScannerPort
from hexa_sec.application.ports.driven.web_scanner_port import WebScannerPort
from hexa_sec.domain.errors import ScannerUnavailableError


class _NoopExecution:
    def execute(self, request: object) -> object:
        raise NotImplementedError


class _NoopImagePolicy:
    def resolve(self, tool: str) -> object | None:
        return None


def test_factory_creates_nmap() -> None:
    adapter = create_scanner_adapter("network_port_discovery", _NoopExecution(), _NoopImagePolicy())
    assert isinstance(adapter, NmapAdapter)
    assert isinstance(adapter, NetworkScannerPort)


def test_factory_creates_nuclei() -> None:
    adapter = create_scanner_adapter("web_cve_templates_nuclei", _NoopExecution(), _NoopImagePolicy())
    assert isinstance(adapter, NucleiAdapter)


def test_factory_creates_burp() -> None:
    adapter = create_scanner_adapter("web_vuln_scan_burp", _NoopExecution(), _NoopImagePolicy())
    assert isinstance(adapter, BurpAdapter)
    assert isinstance(adapter, WebScannerPort)


def test_factory_creates_zap() -> None:
    adapter = create_scanner_adapter("web_vuln_scan_zap", _NoopExecution(), _NoopImagePolicy())
    assert isinstance(adapter, ZapAdapter)
    assert isinstance(adapter, WebScannerPort)


def test_factory_rejects_unknown_vendor() -> None:
    with pytest.raises(ScannerUnavailableError):
        create_scanner_adapter("does-not-exist", _NoopExecution(), _NoopImagePolicy())
