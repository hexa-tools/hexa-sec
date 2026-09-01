"""Tests for ScanStatus (context: scan)."""

from __future__ import annotations

from hexa_sec.domain.scan.scan_status import ScanStatus


def test_scan_status_members() -> None:
    assert ScanStatus.PENDING.value == "pending"
    assert ScanStatus.RUNNING.value == "running"
    assert ScanStatus.DONE.value == "done"
    assert ScanStatus.FAILED.value == "failed"


def test_scan_status_terminal_states() -> None:
    assert ScanStatus.DONE.is_terminal() is True
    assert ScanStatus.FAILED.is_terminal() is True
    assert ScanStatus.PENDING.is_terminal() is False
    assert ScanStatus.RUNNING.is_terminal() is False
