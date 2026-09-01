"""Tests for Dependency (context: dependency_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.dependency_risk.dependency import Dependency


def test_dependency_creation() -> None:
    dep = Dependency(package="requests", version="2.31.0")
    assert dep.version == "2.31.0"


def test_dependency_rejects_empty_package() -> None:
    with pytest.raises(ValueError):
        Dependency(package="", version="1.0")
