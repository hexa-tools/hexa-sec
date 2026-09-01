"""Tests for NetworkScannerPort (driven port)."""

from __future__ import annotations

import inspect

from hexa_sec.application.ports.driven.network_scanner_port import NetworkScannerPort


def test_network_scanner_port_is_abstract() -> None:
    assert inspect.isabstract(NetworkScannerPort) is True
