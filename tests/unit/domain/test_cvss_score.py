"""Tests for CVSSScore (context: vulnerability)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.vulnerability.cvss_score import CVSSScore


def test_cvss_score_valid() -> None:
    score = CVSSScore(base_score=9.8, vector="CVSS:3.1/AV:N")
    assert score.base_score == pytest.approx(9.8)
    assert score.critical() is True


def test_cvss_score_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        CVSSScore(base_score=10.5, vector="")
    with pytest.raises(ValueError):
        CVSSScore(base_score=-1.0, vector="")


def test_cvss_score_severity_tiers() -> None:
    assert CVSSScore(base_score=9.0, vector="").critical() is True
    assert CVSSScore(base_score=7.5, vector="").high() is True
    assert CVSSScore(base_score=5.0, vector="").medium() is True
    assert CVSSScore(base_score=2.0, vector="").low() is True
    assert CVSSScore(base_score=0.0, vector="").critical() is False
