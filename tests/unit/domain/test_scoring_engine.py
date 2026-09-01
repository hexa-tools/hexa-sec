"""Tests for the deterministic scoring engine (context: scoring, SEC-7)."""

from __future__ import annotations

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.scoring.score_components import ScoreComponents
from hexa_sec.domain.scoring.score_level import ScoreLevel
from hexa_sec.domain.scoring.scoring_engine import compute_score


def test_compute_score_full_components_in_range() -> None:
    score = compute_score(
        ScoreComponents(
            severity=Severity.HIGH,
            exploitability=0.8,
            exposure=0.6,
            impact=0.7,
            facility=0.5,
        )
    )
    assert score is not None
    assert 0.0 <= score.value <= 100.0
    assert score.label == ScoreLevel.for_value(score.value).value


def test_compute_score_severity_only_no_invention() -> None:
    score = compute_score(ScoreComponents(severity=Severity.CRITICAL))
    assert score is not None
    assert score.value == 100.0
    assert score.level is ScoreLevel.CRITICAL


def test_compute_score_returns_none_without_components() -> None:
    assert compute_score(ScoreComponents()) is None


def test_compute_score_is_deterministic() -> None:
    components = ScoreComponents(
        severity=Severity.HIGH, exploitability=0.8, exposure=0.6, impact=0.7, facility=0.5
    )
    assert compute_score(components) == compute_score(components)


def test_compute_score_label_matches_level() -> None:
    score = compute_score(
        ScoreComponents(severity=Severity.CRITICAL, exploitability=1.0, exposure=1.0, impact=1.0, facility=1.0)
    )
    assert score is not None
    assert score.label == "critical"
    assert score.level is ScoreLevel.CRITICAL


def test_compute_score_missing_components_weight_renormalized() -> None:
    high_only = compute_score(ScoreComponents(severity=Severity.HIGH))
    assert high_only is not None
    assert high_only.value == 75.0  # rank 3 / 4 -> 0.75 -> 100
