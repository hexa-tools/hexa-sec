"""Tests for the ConfigCheck value object (context: config_risk, SEC-15)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.config_risk.config_check import ConfigCheck


def test_config_check_creation() -> None:
    check = ConfigCheck("1.1.1")
    assert check.identifier == "1.1.1"


def test_config_check_trims_identifier() -> None:
    assert ConfigCheck("  1.1.1  ").identifier == "1.1.1"


def test_config_check_rejects_empty() -> None:
    with pytest.raises(ValueError):
        ConfigCheck("")


def test_config_check_rejects_blank() -> None:
    with pytest.raises(ValueError):
        ConfigCheck("   ")
