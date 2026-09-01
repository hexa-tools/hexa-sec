"""Tests for Authorization (context: consent)."""

from __future__ import annotations

from datetime import date

import pytest

from hexa_sec.domain.consent.authorization import Authorization


def test_authorization_creation() -> None:
    auth = Authorization(
        authorizer="Acme Corp",
        scope="10.0.0.0/24",
        granted_on=date(2026, 1, 1),
        reference="AUTH-0001",
    )
    assert auth.reference == "AUTH-0001"


def test_authorization_rejects_empty_authorizer() -> None:
    with pytest.raises(ValueError):
        Authorization(authorizer="", scope="10.0.0.0/24", granted_on=date(2026, 1, 1), reference="R")


def test_authorization_rejects_empty_scope() -> None:
    with pytest.raises(ValueError):
        Authorization(authorizer="Acme Corp", scope="", granted_on=date(2026, 1, 1), reference="R")
