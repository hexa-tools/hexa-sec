"""Tests for the ImpactLevel enum (context: business_impact, SEC-23)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.business_impact.impact_level import ImpactLevel


def test_impact_level_members() -> None:
    assert ImpactLevel.NORMAL.value == "normal"
    assert ImpactLevel.LOW.value == "low"
    assert ImpactLevel.MEDIUM.value == "medium"
    assert ImpactLevel.HIGH.value == "high"
    assert ImpactLevel.CRITICAL.value == "critical"


def test_impact_level_unique_values() -> None:
    values = [member.value for member in ImpactLevel]
    assert len(values) == len(set(values))


def test_impact_level_normalize_accepts_known() -> None:
    assert ImpactLevel.normalize("normal") is ImpactLevel.NORMAL
    assert ImpactLevel.normalize("HIGH") is ImpactLevel.HIGH
    assert ImpactLevel.normalize("critical") is ImpactLevel.CRITICAL


def test_impact_level_normalize_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="unknown impact level: vital"):
        ImpactLevel.normalize("vital")


def test_impact_level_normalize_rejects_blank() -> None:
    with pytest.raises(ValueError, match="unknown impact level:"):
        ImpactLevel.normalize("   ")


def test_impact_level_rank_ordering() -> None:
    assert ImpactLevel.NORMAL.rank < ImpactLevel.LOW.rank < ImpactLevel.MEDIUM.rank
    assert ImpactLevel.MEDIUM.rank < ImpactLevel.HIGH.rank < ImpactLevel.CRITICAL.rank


def test_impact_level_critical_is_highest() -> None:
    assert ImpactLevel.CRITICAL.rank == max(member.rank for member in ImpactLevel)
    assert ImpactLevel.CRITICAL.is_critical is True
    assert ImpactLevel.HIGH.is_critical is False
