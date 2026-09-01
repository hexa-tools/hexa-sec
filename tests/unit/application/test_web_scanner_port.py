"""Tests for WebScannerPort (driven port)."""

from __future__ import annotations

import inspect

from hexa_sec.application.ports.driven.web_scanner_port import WebScannerPort


def test_web_scanner_port_is_abstract() -> None:
    assert inspect.isabstract(WebScannerPort) is True
