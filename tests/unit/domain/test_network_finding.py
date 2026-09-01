"""Tests for NetworkFinding (context: network_risk, SEC-11)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.asset_inventory.port import Application, Port
from hexa_sec.domain.network_risk.banner import Banner
from hexa_sec.domain.network_risk.exposure import Exposure
from hexa_sec.domain.network_risk.network_finding import NetworkFinding


def _finding(
    ip: str,
    port: int,
    service: str = "ssh",
    banner: str = "SSH-2.0-OpenSSH",
    exposure: Exposure = Exposure.INTERNET_EXPOSED,
) -> NetworkFinding:
    return NetworkFinding(
        asset=ip,
        port=Port(port),
        service=Application(service),
        banner=Banner(banner),
        exposure=exposure,
    )


def test_network_finding_creation() -> None:
    finding = NetworkFinding(
        asset="10.0.0.1",
        port=Port(22),
        service=Application("ssh"),
        banner=Banner("SSH-2.0-OpenSSH"),
        exposure=Exposure.INTERNET_EXPOSED,
    )
    assert finding.asset == "10.0.0.1"
    assert finding.port.number == 22
    assert finding.service.name == "ssh"
    assert finding.banner.text == "SSH-2.0-OpenSSH"
    assert finding.exposure is Exposure.INTERNET_EXPOSED


def test_network_finding_rejects_empty_asset() -> None:
    with pytest.raises(ValueError):
        _finding(ip="", port=22)


def test_network_finding_rejects_whitespace_asset() -> None:
    with pytest.raises(ValueError):
        _finding(ip="   ", port=22)


def test_network_finding_rejects_non_exposure_type() -> None:
    with pytest.raises(ValueError):
        NetworkFinding(
            asset="10.0.0.1",
            port=Port(22),
            service=Application("ssh"),
            banner=Banner("SSH-2.0-OpenSSH"),
            exposure="internet_exposed",
        )


def test_network_finding_port_boundaries() -> None:
    assert _finding(ip="10.0.0.1", port=1).port.number == 1
    assert _finding(ip="10.0.0.1", port=65535).port.number == 65535


@pytest.mark.parametrize("bad_port", [0, 65536, -1, 70000])
def test_network_finding_rejects_out_of_range_port(bad_port: int) -> None:
    with pytest.raises(ValueError):
        _finding(ip="10.0.0.1", port=bad_port)


def test_port_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        Port(0)
    with pytest.raises(ValueError):
        Port(65536)


def test_application_field_normalizes_name() -> None:
    assert _finding(ip="10.0.0.1", port=443, service="HTTPS").service.name == "https"


def test_application_field_rejects_empty() -> None:
    with pytest.raises(ValueError):
        _finding(ip="10.0.0.1", port=443, service="")
