"""Tests for ConfigScannerPort (driven port)."""

from __future__ import annotations

import inspect

from hexa_sec.application.ports.driven.config_scanner_port import ConfigScannerPort


def test_config_scanner_port_is_abstract() -> None:
    assert inspect.isabstract(ConfigScannerPort) is True
