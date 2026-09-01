"""Tests for ScoreComponents (context: scoring, SEC-7)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.scoring.score_components import ScoreComponents


def test_score_components_severity_only() -> None:
    components = ScoreComponents(severity=Severity.HIGH)
    assert components.severity is Severity.HIGH
    assert components.exploitability is None
    assert components.exposure is None
    assert components.impact is None
    assert components.facility is None


def test_score_components_full() -> None:
    components = ScoreComponents(
        severity=Severity.CRITICAL,
        exploitability=0.9,
        exposure=1.0,
        impact=0.8,
        facility=0.4,
    )
    assert components.exploitability == 0.9
    assert components.facility == 0.4


def test_score_components_all_optional() -> None:
    components = ScoreComponents()
    assert components.severity is None


def test_score_components_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        ScoreComponents(severity=Severity.HIGH, exposure=1.5)
    with pytest.raises(ValueError):
        ScoreComponents(severity=Severity.HIGH, facility=-0.1)
