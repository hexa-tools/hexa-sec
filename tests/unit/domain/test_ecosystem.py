"""Tests for the Ecosystem enum (context: dependency_risk, SEC-13)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.dependency_risk.ecosystem import Ecosystem


def test_ecosystem_members() -> None:
    assert Ecosystem.NPM.value == "npm"
    assert Ecosystem.PYPI.value == "pypi"
    assert Ecosystem.MAVEN.value == "maven"
    assert Ecosystem.GEM.value == "gem"
    assert Ecosystem.CARGO.value == "cargo"
    assert Ecosystem.GOLANG.value == "golang"


def test_ecosystem_unique_values() -> None:
    values = [member.value for member in Ecosystem]
    assert len(values) == len(set(values))


def test_ecosystem_normalize_accepts_known_values() -> None:
    assert Ecosystem.normalize("npm") is Ecosystem.NPM
    assert Ecosystem.normalize("  pypi  ") is Ecosystem.PYPI
    assert Ecosystem.normalize("Maven") is Ecosystem.MAVEN
    assert Ecosystem.normalize("golang") is Ecosystem.GOLANG


def test_ecosystem_normalize_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="unknown ecosystem: cobol"):
        Ecosystem.normalize("cobol")


def test_ecosystem_normalize_rejects_blank() -> None:
    with pytest.raises(ValueError, match="unknown ecosystem:"):
        Ecosystem.normalize("   ")
