"""Tests for Severity (context: finding)."""

from __future__ import annotations

from hexa_sec.domain.finding.severity import Severity


def test_severity_ordered_values() -> None:
    assert Severity.CRITICAL.value == "critical"
    assert Severity.INFO.value == "info"


def test_severity_rank_increases_with_severity() -> None:
    assert Severity.INFO.rank < Severity.CRITICAL.rank
    ordered = [Severity.INFO, Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
    assert ordered == sorted(ordered, key=lambda s: s.rank)


def test_severity_parse_unknown_raises() -> None:
    import pytest

    with pytest.raises(ValueError):
        Severity("bogus")
