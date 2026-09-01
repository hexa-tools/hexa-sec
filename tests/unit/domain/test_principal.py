"""Tests for the Principal value object (context: identity_risk, SEC-19)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.identity_risk.principal import Principal


def test_principal_creation() -> None:
    principal = Principal("svc-backup")
    assert principal.value == "svc-backup"


def test_principal_trims_value() -> None:
    assert Principal("  svc-backup  ").value == "svc-backup"


def test_principal_rejects_empty() -> None:
    with pytest.raises(ValueError):
        Principal("")


def test_principal_rejects_blank() -> None:
    with pytest.raises(ValueError):
        Principal("   ")
