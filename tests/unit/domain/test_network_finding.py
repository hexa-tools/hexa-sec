"""Tests for NetworkFinding (context: network_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.network_risk.network_finding import NetworkFinding


def test_network_finding_creation() -> None:
    finding = NetworkFinding(host="10.0.0.1", port=22, service="ssh")
    assert finding.exposed_to_internet is False


def test_network_finding_rejects_empty_host() -> None:
    with pytest.raises(ValueError):
        NetworkFinding(host="", port=443, service="https")


def test_network_finding_rejects_invalid_port() -> None:
    with pytest.raises(ValueError):
        NetworkFinding(host="10.0.0.1", port=70000, service="ssh")


def test_network_finding_rejects_zero_port() -> None:
    with pytest.raises(ValueError):
        NetworkFinding(host="10.0.0.1", port=0, service="ssh")


def test_network_finding_rejects_empty_service() -> None:
    with pytest.raises(ValueError):
        NetworkFinding(host="10.0.0.1", port=22, service="")


def test_network_finding_port_boundaries() -> None:
    assert NetworkFinding(host="10.0.0.1", port=1, service="x").port == 1
    assert NetworkFinding(host="10.0.0.1", port=65535, service="x").port == 65535


def test_network_finding_exposed_flag() -> None:
    finding = NetworkFinding(host="10.0.0.1", port=443, service="https", exposed_to_internet=True)
    assert finding.exposed_to_internet is True
