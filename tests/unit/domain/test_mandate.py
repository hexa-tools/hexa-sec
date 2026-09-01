"""Tests for MandateLevel + MandateId + Mandate (context: consent — law Godfrain)."""

from __future__ import annotations

from datetime import date

import pytest

from hexa_sec.domain.consent.mandate import Mandate, MandateId, MandateLevel


def _mandate(**overrides: object) -> Mandate:
    defaults: dict[str, object] = {
        "mandate_id": MandateId("mnd_0001"),
        "client": "Acme Corp",
        "targets": ("10.0.0.1", "https://app.acme.example"),
        "start_date": date(2026, 1, 1),
        "end_date": date(2026, 12, 31),
        "level": MandateLevel.STANDARD,
        "signature": "REF-2026-0001",
    }
    defaults.update(overrides)
    return Mandate(**defaults)


def test_mandate_creation_and_level() -> None:
    mandate = _mandate()
    assert mandate.level is MandateLevel.STANDARD
    assert mandate.is_offensive() is False


def test_mandate_offensive_level() -> None:
    assert _mandate(level=MandateLevel.OFFENSIVE).is_offensive() is True


def test_mandate_covers_target() -> None:
    mandate = _mandate()
    assert mandate.covers("10.0.0.2") is False
    assert mandate.covers("10.0.0.1") is True
    assert mandate.covers("https://app.acme.example") is True


def test_mandate_valid_within_period() -> None:
    assert _mandate().is_valid(date(2026, 6, 1)) is True


def test_mandate_valid_at_start_boundary() -> None:
    # frontières : exactement au début de validité -> True (bornes incluses)
    assert _mandate().is_valid(date(2026, 1, 1)) is True


def test_mandate_valid_at_end_boundary() -> None:
    # frontières : exactement à la fin de validité -> True (bornes incluses)
    assert _mandate().is_valid(date(2026, 12, 31)) is True


def test_mandate_not_yet_valid_before_start() -> None:
    # frontières : juste avant le début -> False (pas encore valide)
    assert _mandate().is_valid(date(2025, 12, 31)) is False


def test_mandate_expired_after_end() -> None:
    assert _mandate().is_valid(date(2027, 1, 1)) is False


def test_mandate_rejects_empty_targets() -> None:
    with pytest.raises(ValueError):
        _mandate(targets=())


def test_mandate_rejects_end_before_start() -> None:
    with pytest.raises(ValueError):
        _mandate(start_date=date(2026, 12, 31), end_date=date(2026, 1, 1))


def test_mandate_rejects_missing_signature() -> None:
    with pytest.raises(ValueError):
        _mandate(signature="")


def test_mandate_rejects_whitespace_signature() -> None:
    # « signature blanche » -> ValueError (non signé = invalide)
    with pytest.raises(ValueError):
        _mandate(signature="   ")


def test_mandate_rejects_whitespace_client() -> None:
    with pytest.raises(ValueError):
        _mandate(client="   ")
