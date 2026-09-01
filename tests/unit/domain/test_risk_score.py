"""Tests for RiskScore (context: scoring, SEC-7)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.scoring.risk_score import RiskScore
from hexa_sec.domain.scoring.score_level import ScoreLevel


def test_risk_score_creation() -> None:
    score = RiskScore(value=62.0, label="moderate")
    assert score.value == 62.0
    assert score.label == "moderate"


def test_risk_score_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        RiskScore(value=101.0, label="moderate")
    with pytest.raises(ValueError):
        RiskScore(value=-1.0, label="moderate")


def test_risk_score_rejects_whitespace_label() -> None:
    with pytest.raises(ValueError):
        RiskScore(value=50.0, label="   ")


def test_risk_score_bounds_inclusive() -> None:
    assert RiskScore(value=0.0, label="low").value == 0.0
    assert RiskScore(value=100.0, label="critical").value == 100.0


def test_risk_score_level_derived_from_value() -> None:
    assert RiskScore(value=95.0, label="critical").level is ScoreLevel.CRITICAL
    assert RiskScore(value=62.0, label="moderate").level is ScoreLevel.HIGH
    assert RiskScore(value=40.0, label="moderate").level is ScoreLevel.MODERATE


def test_risk_score_from_value_derives_label() -> None:
    assert RiskScore.from_value(95.0).label == "critical"
    assert RiskScore.from_value(62.0).label == "high"
    assert RiskScore.from_value(0.0).label == "low"
    assert RiskScore.from_value(100.0).label == "critical"


def test_risk_score_from_value_accepts_bounds() -> None:
    assert RiskScore.from_value(0.0).value == 0.0
    assert RiskScore.from_value(100.0).value == 100.0


def test_risk_score_from_value_is_coherent() -> None:
    # catégorie « cohérence » : from_value produit un label cohérent avec la valeur
    assert RiskScore.from_value(95.0).is_coherent() is True
    assert RiskScore.from_value(0.0).is_coherent() is True


def test_risk_score_detects_incoherent_label() -> None:
    # catégorie « invariant » : un label qui contredit la valeur est détectable
    inconsistent = RiskScore(value=95.0, label="low")
    assert inconsistent.level is ScoreLevel.CRITICAL
    assert inconsistent.is_coherent() is False
