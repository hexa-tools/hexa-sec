"""Tests for ScanWindow (context: scan)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.scan.scan_window import ScanWindow


def test_scan_window_creation() -> None:
    window = ScanWindow(start_hour=22, end_hour=6)
    assert window.start_hour == 22
    assert window.end_hour == 6


def test_scan_window_duration() -> None:
    assert ScanWindow(start_hour=2, end_hour=6).duration() == 4
    assert ScanWindow(start_hour=22, end_hour=6).duration() == 8


def test_scan_window_is_night() -> None:
    assert ScanWindow(start_hour=22, end_hour=6).is_night() is True
    assert ScanWindow(start_hour=2, end_hour=5).is_night() is True
    assert ScanWindow(start_hour=9, end_hour=17).is_night() is False


def test_scan_window_rejects_out_of_range_hours() -> None:
    with pytest.raises(ValueError):
        ScanWindow(start_hour=-1, end_hour=6)
    with pytest.raises(ValueError):
        ScanWindow(start_hour=0, end_hour=24)
    with pytest.raises(ValueError):
        ScanWindow(start_hour=24, end_hour=6)


def test_scan_window_rejects_empty_window() -> None:
    with pytest.raises(ValueError):
        ScanWindow(start_hour=6, end_hour=6)
