"""Tests for EPSSScore (context: vulnerability)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.vulnerability.epss_score import EPSSScore


def test_epss_probability_bounds() -> None:
    assert EPSSScore(probability=0.5).probability == pytest.approx(0.5)
    assert EPSSScore(probability=0.0).probability == 0.0
    assert EPSSScore(probability=1.0).probability == 1.0


def test_epss_rejects_out_of_bounds() -> None:
    with pytest.raises(ValueError):
        EPSSScore(probability=-0.1)
    with pytest.raises(ValueError):
        EPSSScore(probability=1.1)


def test_epss_exploitable_at_default_threshold() -> None:
    assert EPSSScore(probability=0.85).exploitable() is True
    assert EPSSScore(probability=0.05).exploitable() is False
