"""Tests for CodeFinding (context: code_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.code_risk.code_finding import CodeFinding


def test_code_finding_creation() -> None:
    finding = CodeFinding(path="src/app.py", rule_id="bandit:B307")
    assert finding.rule_id == "bandit:B307"


def test_code_finding_rejects_empty_rule() -> None:
    with pytest.raises(ValueError):
        CodeFinding(path="src/app.py", rule_id="")


def test_code_finding_rejects_empty_path() -> None:
    with pytest.raises(ValueError):
        CodeFinding(path="", rule_id="bandit:B307")
