"""Tests for the Effort value object (context: remediation, SEC-24)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.remediation.effort import Effort


def test_effort_creation() -> None:
    assert Effort(30).minutes == 30


def test_effort_rejects_negative() -> None:
    with pytest.raises(ValueError):
        Effort(-5)


def test_effort_readable_hours_and_minutes() -> None:
    assert Effort(150).readable() == "2h30"


def test_effort_readable_minutes_only() -> None:
    assert Effort(45).readable() == "45 min"


def test_effort_readable_hours_only() -> None:
    assert Effort(120).readable() == "2h"


def test_effort_readable_zero() -> None:
    assert Effort(0).readable() == "0 min"
