"""Tests for MandateRepositoryPort (US-1, driven port)."""

from __future__ import annotations

from datetime import date

from hexa_sec.application.ports.driven.mandate_repository_port import MandateRepositoryPort
from hexa_sec.domain.consent.mandate import Mandate, MandateId, MandateLevel


class _FakeRepo(MandateRepositoryPort):
    def __init__(self, mandate: Mandate | None) -> None:
        self._mandate = mandate

    def load(self, mandate_id: str) -> Mandate | None:
        return self._mandate


def _mandate() -> Mandate:
    return Mandate(
        mandate_id=MandateId("mnd_0001"),
        client="Acme Corp",
        targets=("10.0.0.1",),
        start_date=date(2000, 1, 1),
        end_date=date(2100, 12, 31),
        level=MandateLevel.STANDARD,
        signature="REF-2026-0001",
    )


def test_repository_resolves_mandate() -> None:
    mandate = _mandate()
    assert _FakeRepo(mandate).load("mnd_0001") is mandate


def test_repository_fail_closed_on_unknown() -> None:
    assert _FakeRepo(None).load("mnd_9999") is None
