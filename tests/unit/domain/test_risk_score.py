"""Tests for RiskScore (context: scoring)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.scoring.risk_score import RiskScore


def test_risk_score_creation() -> None:
    score = RiskScore(value=62.0, label="moderate")
    assert score.value == 62.0
    assert score.label == "moderate"


def test_risk_score_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        RiskScore(value=101.0, label="moderate")
    with pytest.raises(ValueError):
        RiskScore(value=-1.0, label="moderate")
