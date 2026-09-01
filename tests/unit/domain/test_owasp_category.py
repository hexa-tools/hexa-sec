"""Tests for OwaspApiCategory (context: api_risk)."""

from __future__ import annotations

from hexa_sec.domain.api_risk.owasp_category import OwaspApiCategory


def test_owasp_api_category_covers_top_ten() -> None:
    assert len(list(OwaspApiCategory)) == 10


def test_owasp_api_category_values_are_unique() -> None:
    values = [member.value for member in OwaspApiCategory]
    assert len(values) == len(set(values))


def test_owasp_api_category_first_entry() -> None:
    assert OwaspApiCategory.BROKEN_OBJECT_LEVEL_AUTHORIZATION.value == "api1"
