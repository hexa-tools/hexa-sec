"""Tests for SecretType (context: secret_risk)."""

from __future__ import annotations

from hexa_sec.domain.secret_risk.secret_type import SecretType


def test_secret_type_members() -> None:
    assert SecretType.API_KEY.value == "api_key"
    assert SecretType.PASSWORD.value == "password"
    assert SecretType.TOKEN.value == "token"


def test_secret_type_is_unique() -> None:
    values = [member.value for member in SecretType]
    assert len(values) == len(set(values))
