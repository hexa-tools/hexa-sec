"""Tests for RemediationStatus (context: remediation, SEC-24)."""

from __future__ import annotations

from hexa_sec.domain.remediation.remediation_status import RemediationStatus


def test_remediation_status_members() -> None:
    assert RemediationStatus.OPEN.value == "open"
    assert RemediationStatus.FIXED.value == "fixed"
    assert RemediationStatus.IN_PROGRESS.value == "in_progress"
    assert RemediationStatus.ACCEPTED.value == "accepted"


def test_remediation_status_resolved() -> None:
    assert RemediationStatus.FIXED.is_resolved() is True
    assert RemediationStatus.ACCEPTED.is_resolved() is True
    assert RemediationStatus.OPEN.is_resolved() is False
    assert RemediationStatus.IN_PROGRESS.is_resolved() is False


def test_remediation_status_can_transition() -> None:
    assert RemediationStatus.OPEN.can_transition_to(RemediationStatus.IN_PROGRESS) is True
    assert RemediationStatus.OPEN.can_transition_to(RemediationStatus.ACCEPTED) is True
    assert RemediationStatus.OPEN.can_transition_to(RemediationStatus.FIXED) is False
    assert RemediationStatus.IN_PROGRESS.can_transition_to(RemediationStatus.FIXED) is True
    assert RemediationStatus.IN_PROGRESS.can_transition_to(RemediationStatus.ACCEPTED) is True
    assert RemediationStatus.FIXED.can_transition_to(RemediationStatus.OPEN) is False
    assert RemediationStatus.ACCEPTED.can_transition_to(RemediationStatus.IN_PROGRESS) is False
