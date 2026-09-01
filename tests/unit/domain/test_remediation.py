"""Tests for Remediation (context: remediation, SEC-24)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.remediation.effort import Effort
from hexa_sec.domain.remediation.priority import Priority
from hexa_sec.domain.remediation.remediation import Remediation
from hexa_sec.domain.remediation.remediation_status import RemediationStatus


def _remediation(
    finding_id: str = "fnd_0001",
    instruction: str = "Upgrade to 1.2.0",
    status: RemediationStatus = RemediationStatus.OPEN,
    effort: Effort | None = Effort(30),
    priority: Priority | None = Priority.HIGH,
) -> Remediation:
    return Remediation(
        finding_id=finding_id,
        instruction=instruction,
        status=status,
        effort=effort,
        priority=priority,
    )


def test_remediation_creation() -> None:
    remediation = _remediation()
    assert remediation.finding_id == "fnd_0001"
    assert remediation.instruction == "Upgrade to 1.2.0"
    assert remediation.status is RemediationStatus.OPEN
    assert remediation.effort == Effort(30)
    assert remediation.priority is Priority.HIGH


def test_remediation_without_effort_priority() -> None:
    remediation = Remediation(finding_id="fnd_0001", instruction="Upgrade to 1.2.0")
    assert remediation.effort is None
    assert remediation.priority is None


def test_remediation_normalizes_fields() -> None:
    remediation = _remediation(finding_id="  fnd_0001  ", instruction="  Upgrade  ")
    assert remediation.finding_id == "fnd_0001"
    assert remediation.instruction == "Upgrade"


def test_remediation_rejects_empty_finding_id() -> None:
    with pytest.raises(ValueError):
        _remediation(finding_id="")


def test_remediation_rejects_blank_finding_id() -> None:
    with pytest.raises(ValueError):
        _remediation(finding_id="   ")


def test_remediation_rejects_empty_instruction() -> None:
    with pytest.raises(ValueError):
        _remediation(instruction="")


def test_remediation_rejects_blank_instruction() -> None:
    with pytest.raises(ValueError):
        _remediation(instruction="   ")


def test_remediation_rejects_non_status() -> None:
    with pytest.raises(ValueError):
        _remediation(status="open")


def test_remediation_rejects_non_effort() -> None:
    with pytest.raises(ValueError):
        _remediation(effort="30")  # type: ignore[arg-type]


def test_remediation_rejects_non_priority() -> None:
    with pytest.raises(ValueError):
        _remediation(priority="high")  # type: ignore[arg-type]


def test_remediation_rejects_terminal_status_construction() -> None:
    with pytest.raises(ValueError):
        _remediation(status=RemediationStatus.FIXED)
    with pytest.raises(ValueError):
        _remediation(status=RemediationStatus.ACCEPTED)


def test_remediation_transition_open_to_in_progress() -> None:
    updated = _remediation().transition_to(RemediationStatus.IN_PROGRESS)
    assert updated.status is RemediationStatus.IN_PROGRESS
    assert updated.finding_id == "fnd_0001"


def test_remediation_transition_in_progress_to_fixed() -> None:
    in_progress = _remediation().transition_to(RemediationStatus.IN_PROGRESS)
    fixed = in_progress.transition_to(RemediationStatus.FIXED)
    assert fixed.status.is_resolved() is True


def test_remediation_transition_accepts_risk_from_open() -> None:
    accepted = _remediation().transition_to(RemediationStatus.ACCEPTED)
    assert accepted.status.is_resolved() is True


def test_remediation_transition_in_progress_to_accepted() -> None:
    in_progress = _remediation().transition_to(RemediationStatus.IN_PROGRESS)
    accepted = in_progress.transition_to(RemediationStatus.ACCEPTED)
    assert accepted.status.is_resolved() is True


def test_remediation_transition_from_fixed_is_rejected() -> None:
    fixed = (
        _remediation()
        .transition_to(RemediationStatus.IN_PROGRESS)
        .transition_to(RemediationStatus.FIXED)
    )
    with pytest.raises(ValueError):
        fixed.transition_to(RemediationStatus.OPEN)
    with pytest.raises(ValueError):
        fixed.transition_to(RemediationStatus.ACCEPTED)


def test_remediation_transition_from_accepted_is_rejected() -> None:
    accepted = _remediation().transition_to(RemediationStatus.ACCEPTED)
    with pytest.raises(ValueError):
        accepted.transition_to(RemediationStatus.IN_PROGRESS)


def test_remediation_transition_illegal_open_to_fixed() -> None:
    with pytest.raises(ValueError):
        _remediation().transition_to(RemediationStatus.FIXED)


def test_remediation_transition_illegal_same_status() -> None:
    with pytest.raises(ValueError):
        _remediation().transition_to(RemediationStatus.OPEN)


def test_remediation_transition_rejects_non_status() -> None:
    with pytest.raises(ValueError):
        _remediation().transition_to("fixed")  # type: ignore[arg-type]


def test_remediation_transition_preserves_effort_priority() -> None:
    updated = _remediation().transition_to(RemediationStatus.IN_PROGRESS)
    assert updated.effort == Effort(30)
    assert updated.priority is Priority.HIGH
