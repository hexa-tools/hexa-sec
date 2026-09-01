"""Tests for RemediationStatus (context: remediation)."""

from __future__ import annotations

from hexa_sec.domain.remediation.remediation_status import RemediationStatus


def test_remediation_status_members() -> None:
    assert RemediationStatus.OPEN.value == "open"
    assert RemediationStatus.FIXED.value == "fixed"
    assert RemediationStatus.IN_PROGRESS.value == "in_progress"
    assert RemediationStatus.ACCEPTED.value == "accepted"


def test_remediation_status_resolved() -> None:
    assert RemediationStatus.FIXED.is_resolved() is True
    assert RemediationStatus.OPEN.is_resolved() is False
