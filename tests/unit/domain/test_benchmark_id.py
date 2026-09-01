"""Tests for the BenchmarkId value object (context: config_risk, SEC-15)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.config_risk.benchmark_id import BenchmarkId


def test_benchmark_id_normalizes_fields() -> None:
    benchmark = BenchmarkId("  cis_ubuntu_22.04  ", "  CIS Ubuntu 22.04  ")
    assert benchmark.identifier == "cis_ubuntu_22.04"
    assert benchmark.description == "CIS Ubuntu 22.04"


def test_benchmark_id_rejects_empty_identifier() -> None:
    with pytest.raises(ValueError):
        BenchmarkId("", "CIS Ubuntu 22.04")
    with pytest.raises(ValueError):
        BenchmarkId("   ", "CIS Ubuntu 22.04")


def test_benchmark_id_rejects_blank_description() -> None:
    with pytest.raises(ValueError):
        BenchmarkId("cis_ubuntu_22.04", "")
    with pytest.raises(ValueError):
        BenchmarkId("cis_ubuntu_22.04", "   ")
