"""Tests for ScoreLevel thresholds (context: scoring, SEC-7)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.scoring.score_level import ScoreLevel


def test_score_level_members() -> None:
    assert ScoreLevel.CRITICAL.value == "critical"
    assert ScoreLevel.HIGH.value == "high"
    assert ScoreLevel.MODERATE.value == "moderate"
    assert ScoreLevel.LOW.value == "low"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (100.0, ScoreLevel.CRITICAL),
        (95.0, ScoreLevel.CRITICAL),
        (80.0, ScoreLevel.CRITICAL),
        (79.9, ScoreLevel.HIGH),
        (60.0, ScoreLevel.HIGH),
        (59.9, ScoreLevel.MODERATE),
        (40.0, ScoreLevel.MODERATE),
        (39.9, ScoreLevel.LOW),
        (0.0, ScoreLevel.LOW),
    ],
)
def test_score_level_for_value_thresholds(value: float, expected: ScoreLevel) -> None:
    assert ScoreLevel.for_value(value) is expected


def test_score_level_frontier_is_inclusive_upward() -> None:
    # catégorie « frontières » : à la borne, le niveau supérieur est retenu (>=)
    assert ScoreLevel.for_value(80.0) is ScoreLevel.CRITICAL
    assert ScoreLevel.for_value(60.0) is ScoreLevel.HIGH
    assert ScoreLevel.for_value(40.0) is ScoreLevel.MODERATE
