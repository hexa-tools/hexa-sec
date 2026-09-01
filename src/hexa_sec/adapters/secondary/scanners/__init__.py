"""Scanner adapter factory (one adapter per tool)."""

from __future__ import annotations

from hexa_sec.adapters.secondary.scanners.scanner_factory import create_scanner_adapter

__all__ = ["create_scanner_adapter"]
