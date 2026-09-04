"""Tests for OwaspApiCategory (OWASP API Top 10) — context: api_risk, SEC-30."""

from __future__ import annotations

import pytest

from hexa_sec.domain.api_risk.owasp_category import OwaspApiCategory


def test_members() -> None:
    assert OwaspApiCategory.BROKEN_OBJECT_LEVEL_AUTHORIZATION.value == "api1"
    assert OwaspApiCategory.UNSAFE_CONSUMPTION_OF_APIS.value == "api10"


def test_has_exactly_ten() -> None:
    assert len(list(OwaspApiCategory)) == 10


def test_normalize_accepts_codes() -> None:
    assert OwaspApiCategory.normalize("api1") is OwaspApiCategory.BROKEN_OBJECT_LEVEL_AUTHORIZATION
    assert OwaspApiCategory.normalize("API1") is OwaspApiCategory.BROKEN_OBJECT_LEVEL_AUTHORIZATION
    assert (
        OwaspApiCategory.normalize("api05") is OwaspApiCategory.BROKEN_FUNCTION_LEVEL_AUTHORIZATION
    )
    assert OwaspApiCategory.normalize("10") is OwaspApiCategory.UNSAFE_CONSUMPTION_OF_APIS


def test_normalize_rejects_unknown() -> None:
    with pytest.raises(ValueError):
        OwaspApiCategory.normalize("api11")
    with pytest.raises(ValueError):
        OwaspApiCategory.normalize("bogus")


def test_normalize_rejects_unknown_with_stable_message() -> None:
    # hors bornes (api11) et non-chiffres (bogus) rejetés avec un message stable
    with pytest.raises(ValueError, match="unknown OWASP API category: api11"):
        OwaspApiCategory.normalize("api11")
    with pytest.raises(ValueError, match="unknown OWASP API category: bogus"):
        OwaspApiCategory.normalize("bogus")
