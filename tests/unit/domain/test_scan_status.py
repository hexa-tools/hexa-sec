"""Tests for ScanStatus transitions (context: scan, SEC-4)."""

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


def test_scan_status_allowed_transitions() -> None:
    assert ScanStatus.PENDING.can_transition_to(ScanStatus.RUNNING) is True
    assert ScanStatus.RUNNING.can_transition_to(ScanStatus.DONE) is True
    assert ScanStatus.RUNNING.can_transition_to(ScanStatus.FAILED) is True


def test_scan_status_rejected_transitions() -> None:
    assert ScanStatus.PENDING.can_transition_to(ScanStatus.DONE) is False
    assert ScanStatus.PENDING.can_transition_to(ScanStatus.FAILED) is False
    assert ScanStatus.DONE.can_transition_to(ScanStatus.PENDING) is False
    assert ScanStatus.DONE.can_transition_to(ScanStatus.DONE) is False
    assert ScanStatus.FAILED.can_transition_to(ScanStatus.RUNNING) is False
