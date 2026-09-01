"""Tests for PriorityAction (context: report, SEC-8)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.report.priority_action import PriorityAction
from hexa_sec.domain.scoring.risk_score import RiskScore


def _action(**overrides: object) -> PriorityAction:
    defaults: dict[str, object] = {
        "finding_id": FindingId("fnd_0001"),
        "issue": "Exposed API key",
        "why": "An attacker can take over the account",
        "fix": "Rotate the key immediately",
        "effort": "5 min",
        "risk_score": RiskScore.from_value(95.0),
    }
    defaults.update(overrides)
    return PriorityAction(**defaults)


def test_priority_action_creation() -> None:
    action = _action()
    assert action.finding_id == FindingId("fnd_0001")
    assert action.issue == "Exposed API key"
    assert action.effort == "5 min"
    assert action.risk_score.value == 95.0


def test_priority_action_requires_a_finding() -> None:
    # pas de spéculation : une action doit pointer vers un finding réel
    with pytest.raises(ValueError):
        _action(finding_id=None)


def test_priority_action_rejects_empty_issue() -> None:
    with pytest.raises(ValueError):
        _action(issue="")


def test_priority_action_rejects_empty_why() -> None:
    with pytest.raises(ValueError):
        _action(why="   ")


def test_priority_action_rejects_empty_fix() -> None:
    with pytest.raises(ValueError):
        _action(fix="")


def test_priority_action_requires_effort() -> None:
    # pas de fix sans effort (pas de spéculation)
    with pytest.raises(ValueError):
        _action(effort="")
