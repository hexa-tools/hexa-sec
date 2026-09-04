"""Tests for the Priority enum (context: remediation, SEC-24)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.remediation.priority import Priority


def test_priority_members() -> None:
    assert Priority.HIGH.value == "high"
    assert Priority.MEDIUM.value == "medium"
    assert Priority.LOW.value == "low"


def test_priority_unique_values() -> None:
    values = [member.value for member in Priority]
    assert len(values) == len(set(values))


def test_priority_normalize_accepts_known() -> None:
    assert Priority.normalize("high") is Priority.HIGH
    assert Priority.normalize("MEDIUM") is Priority.MEDIUM
    assert Priority.normalize("low") is Priority.LOW


def test_priority_normalize_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="unknown priority: urgent"):
        Priority.normalize("urgent")


def test_priority_normalize_rejects_blank() -> None:
    with pytest.raises(ValueError, match="unknown priority:"):
        Priority.normalize("   ")


def test_priority_rank_order() -> None:
    assert Priority.LOW.rank < Priority.MEDIUM.rank < Priority.HIGH.rank
