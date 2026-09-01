"""Tests for the RuleId value object (context: code_risk, SEC-14)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.code_risk.rule_id import RuleId


def test_rule_id_normalizes_fields() -> None:
    rule = RuleId("  bandit.B101  ", "  Assert used  ")
    assert rule.identifier == "bandit.B101"
    assert rule.description == "Assert used"


def test_rule_id_rejects_empty_identifier() -> None:
    with pytest.raises(ValueError):
        RuleId("", "Assert used")
    with pytest.raises(ValueError):
        RuleId("   ", "Assert used")


def test_rule_id_rejects_blank_description() -> None:
    with pytest.raises(ValueError):
        RuleId("bandit.B101", "")
    with pytest.raises(ValueError):
        RuleId("bandit.B101", "   ")
