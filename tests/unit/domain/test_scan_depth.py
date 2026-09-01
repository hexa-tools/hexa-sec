"""Tests for ScanDepth (context: scan)."""

from __future__ import annotations

from hexa_sec.domain.scan.scan_depth import ScanDepth


def test_scan_depth_values() -> None:
    assert ScanDepth.QUICK.value == "quick"
    assert ScanDepth.COMPLETE.value == "complete"
    assert ScanDepth.OFFENSIVE.value == "offensive"


def test_scan_depth_is_unique() -> None:
    values = [member.value for member in ScanDepth]
    assert len(values) == len(set(values))


def test_scan_depth_requires_offensive_mandate() -> None:
    assert ScanDepth.OFFENSIVE.requires_offensive_mandate() is True
    assert ScanDepth.QUICK.requires_offensive_mandate() is False
    assert ScanDepth.COMPLETE.requires_offensive_mandate() is False
