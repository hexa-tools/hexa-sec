"""Tests for the SecretType enum (context: secret_risk, SEC-12)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.secret_risk.secret_type import SecretType


def test_secret_type_members() -> None:
    assert SecretType.APIKEY.value == "api_key"
    assert SecretType.PRIVATEKEY.value == "private_key"
    assert SecretType.PASSWORD.value == "password"
    assert SecretType.TOKEN.value == "token"
    assert SecretType.AWSKEY.value == "aws_key"
    assert SecretType.CIPHERTEXT.value == "ciphertext"


def test_secret_type_unique_values() -> None:
    values = [member.value for member in SecretType]
    assert len(values) == len(set(values))


def test_secret_type_normalize_accepts_known_values() -> None:
    assert SecretType.normalize("aws_key") is SecretType.AWSKEY
    assert SecretType.normalize("PRIVATE KEY") is SecretType.PRIVATEKEY
    assert SecretType.normalize("api-key") is SecretType.APIKEY
    assert SecretType.normalize("  token  ") is SecretType.TOKEN
    assert SecretType.normalize("ciphertext") is SecretType.CIPHERTEXT


def test_secret_type_normalize_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="unknown secret type: beyond_the_veil"):
        SecretType.normalize("beyond_the_veil")


def test_secret_type_normalize_rejects_blank() -> None:
    with pytest.raises(ValueError, match="unknown secret type:"):
        SecretType.normalize("   ")
