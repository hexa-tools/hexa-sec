"""Tests for CodeScannerPort (driven port)."""

from __future__ import annotations

import inspect

from hexa_sec.application.ports.driven.code_scanner_port import CodeScannerPort


def test_code_scanner_port_is_abstract() -> None:
    assert inspect.isabstract(CodeScannerPort) is True
