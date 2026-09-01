"""Tests for the Exposure enum (context: network_risk, SEC-11)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.network_risk.exposure import Exposure


def test_exposure_values() -> None:
    assert Exposure.INTERNET_EXPOSED.value == "internet_exposed"
    assert Exposure.INTERNAL_ONLY.value == "internal_only"


def test_exposure_is_exposed() -> None:
    assert Exposure.INTERNET_EXPOSED.is_exposed() is True
    assert Exposure.INTERNAL_ONLY.is_exposed() is False


def test_exposure_normalize_accepts_known_values() -> None:
    assert Exposure.normalize("INTERNAL_ONLY") is Exposure.INTERNAL_ONLY
    assert Exposure.normalize("Internet Exposed") is Exposure.INTERNET_EXPOSED
    assert Exposure.normalize("internet-exposed") is Exposure.INTERNET_EXPOSED
    assert Exposure.normalize("internal_only") is Exposure.INTERNAL_ONLY


def test_exposure_normalize_rejects_unknown() -> None:
    with pytest.raises(ValueError):
        Exposure.normalize("hyperspace")


def test_exposure_normalize_rejects_blank() -> None:
    with pytest.raises(ValueError):
        Exposure.normalize("   ")
