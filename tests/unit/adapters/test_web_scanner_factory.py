"""Tests for the web scanner factory."""

from __future__ import annotations

import pytest

from hexa_sec.adapters.secondary.scanners.web.web_scanner_factory import create_web_scanner
from hexa_sec.application.ports.driven.web_scanner_port import WebScannerPort
from hexa_sec.domain.errors import ScannerUnavailableError


def test_create_web_scanner_known_vendor() -> None:
    adapter = create_web_scanner("nuclei")
    assert isinstance(adapter, WebScannerPort)


def test_create_web_scanner_unknown_vendor() -> None:
    with pytest.raises(ScannerUnavailableError):
        create_web_scanner("does-not-exist")
