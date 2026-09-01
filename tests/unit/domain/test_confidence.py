"""Tests for Confidence (context: finding)."""

from __future__ import annotations

from hexa_sec.domain.finding.confidence import Confidence


def test_confidence_levels() -> None:
    assert Confidence.CERTAIN.value == "certain"
    assert Confidence.GUESS.value == "guess"


def test_confidence_rank_increases_with_certainty() -> None:
    assert Confidence.CERTAIN.rank > Confidence.GUESS.rank
