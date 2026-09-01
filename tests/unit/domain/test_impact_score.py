"""Tests for ImpactScore (context: correlation)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.correlation.impact_score import ImpactLevel, ImpactScore


def test_impact_score_value() -> None:
    assert ImpactScore(value=0.85).value == pytest.approx(0.85)


def test_impact_score_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        ImpactScore(value=1.5)
    with pytest.raises(ValueError):
        ImpactScore(value=-0.1)


def test_impact_score_levels() -> None:
    assert ImpactScore(value=0.9).level() is ImpactLevel.CRITICAL
    assert ImpactScore(value=0.7).level() is ImpactLevel.HIGH
    assert ImpactScore(value=0.4).level() is ImpactLevel.MEDIUM
    assert ImpactScore(value=0.1).level() is ImpactLevel.LOW
