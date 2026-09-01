"""Tests for ConfigFinding (context: config_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.config_risk.config_finding import ConfigFinding


def test_config_finding_creation() -> None:
    finding = ConfigFinding(benchmark="cis_ubuntu_22.04", check="1.1.1")
    assert finding.check == "1.1.1"


def test_config_finding_rejects_empty_benchmark() -> None:
    with pytest.raises(ValueError):
        ConfigFinding(benchmark="", check="1.1.1")


def test_config_finding_rejects_empty_check() -> None:
    with pytest.raises(ValueError):
        ConfigFinding(benchmark="cis_ubuntu_22.04", check="")
