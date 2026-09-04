"""Tests for OwaspCategory (OWASP Top 10) — context: web_risk, SEC-10."""

from __future__ import annotations

import pytest

from hexa_sec.domain.web_risk.owasp_category import OwaspCategory


def test_top_ten_members() -> None:
    assert OwaspCategory.BROKEN_ACCESS_CONTROL.value == "a01"
    assert OwaspCategory.INJECTION.value == "a03"
    assert OwaspCategory.SERVER_SIDE_REQUEST_FORGERY.value == "a10"


def test_top_ten_has_exactly_ten() -> None:
    assert len(list(OwaspCategory)) == 10


def test_order_ascending() -> None:
    ordered = sorted(OwaspCategory, key=lambda c: c.order)
    assert [c.order for c in ordered] == list(range(1, 11))
    assert ordered[0] is OwaspCategory.BROKEN_ACCESS_CONTROL
    assert ordered[-1] is OwaspCategory.SERVER_SIDE_REQUEST_FORGERY


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("A01", OwaspCategory.BROKEN_ACCESS_CONTROL),
        ("a01", OwaspCategory.BROKEN_ACCESS_CONTROL),
        ("A03", OwaspCategory.INJECTION),
        ("A05", OwaspCategory.SECURITY_MISCONFIGURATION),
        ("A10", OwaspCategory.SERVER_SIDE_REQUEST_FORGERY),
    ],
)
def test_normalize_accepts_codes(raw: str, expected: OwaspCategory) -> None:
    assert OwaspCategory.normalize(raw) is expected


def test_normalize_rejects_unknown() -> None:
    # catégorie inconnue -> rejet à la normalisation, jamais devinée
    with pytest.raises(ValueError):
        OwaspCategory.normalize("A99")
    with pytest.raises(ValueError):
        OwaspCategory.normalize("bogus")


def test_normalize_distinguishes_malformed_from_unknown() -> None:
    # malformé (préfixe a non suivi de chiffres) vs bien formé mais inconnu
    with pytest.raises(ValueError, match="invalid OWASP category: a0x"):
        OwaspCategory.normalize("a0x")
    with pytest.raises(ValueError, match="unknown OWASP category: a99"):
        OwaspCategory.normalize("a99")
    with pytest.raises(ValueError, match="unknown OWASP category: a1"):
        OwaspCategory.normalize("a1")


def test_from_code_roundtrip() -> None:
    assert OwaspCategory.from_code("a01") is OwaspCategory.BROKEN_ACCESS_CONTROL
