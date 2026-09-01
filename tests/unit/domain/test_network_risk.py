"""Tests for the NetworkRisk inventory aggregate (context: network_risk, SEC-11)."""

from __future__ import annotations

from hexa_sec.domain.asset_inventory.port import Application, Port
from hexa_sec.domain.network_risk.banner import Banner
from hexa_sec.domain.network_risk.exposure import Exposure
from hexa_sec.domain.network_risk.network_finding import NetworkFinding
from hexa_sec.domain.network_risk.network_risk import NetworkRisk


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


def test_for_asset_consolidates_three_findings_same_host() -> None:
    findings = (
        _finding(ip="10.0.0.1", port=22, service="ssh"),
        _finding(ip="10.0.0.1", port=443, service="https"),
        _finding(ip="10.0.0.1", port=3306, service="mysql", exposure=Exposure.INTERNAL_ONLY),
    )
    inventory = NetworkRisk.for_asset("10.0.0.1", findings)
    assert inventory.asset == "10.0.0.1"
    assert len(inventory.findings) == 3
    assert inventory.exposed_count == 2
    assert inventory.exposed_ports == (22, 443)


def test_for_asset_deduplicates_identical_findings() -> None:
    findings = (
        _finding(ip="10.0.0.1", port=22, service="ssh", banner="first"),
        _finding(ip="10.0.0.1", port=22, service="ssh", banner="second"),
    )
    inventory = NetworkRisk.for_asset("10.0.0.1", findings)
    assert len(inventory.findings) == 1
    assert inventory.findings[0].banner.text == "first"


def test_for_asset_rejects_finding_without_evidence() -> None:
    speculative = _finding(ip="10.0.0.1", port=22, banner="")
    inventory = NetworkRisk.for_asset("10.0.0.1", (speculative,))
    assert inventory.findings == ()
    assert inventory.exposed_count == 0


def test_for_asset_no_findings_returns_empty_inventory() -> None:
    inventory = NetworkRisk.for_asset("10.0.0.1", ())
    assert inventory.findings == ()
    assert inventory.exposed_count == 0
    assert inventory.exposed_ports == ()


def test_for_asset_exposed_ports_sorted_only_exposed() -> None:
    findings = (
        _finding(ip="10.0.0.1", port=8080, service="http"),
        _finding(ip="10.0.0.1", port=22, service="ssh"),
        _finding(ip="10.0.0.1", port=5432, service="postgres", exposure=Exposure.INTERNAL_ONLY),
    )
    inventory = NetworkRisk.for_asset("10.0.0.1", findings)
    assert inventory.exposed_ports == (22, 8080)
    assert inventory.exposed_count == 2


def test_for_asset_zero_exposed() -> None:
    findings = (
        _finding(ip="10.0.0.1", port=5432, service="postgres", exposure=Exposure.INTERNAL_ONLY),
    )
    inventory = NetworkRisk.for_asset("10.0.0.1", findings)
    assert inventory.exposed_ports == ()
    assert inventory.exposed_count == 0


# --- Category: invariant métier / agrégation par asset ----------------------


def test_for_asset_ignores_findings_of_other_asset() -> None:
    findings = (_finding(ip="10.0.0.2", port=22, service="ssh"),)
    inventory = NetworkRisk.for_asset("10.0.0.1", findings)
    assert inventory.findings == ()
    assert inventory.exposed_count == 0
    assert inventory.exposed_ports == ()


def test_for_asset_ignores_other_asset_among_own() -> None:
    findings = (
        _finding(ip="10.0.0.1", port=22, service="ssh"),
        _finding(ip="10.0.0.2", port=443, service="https"),
    )
    inventory = NetworkRisk.for_asset("10.0.0.1", findings)
    assert [f.port.number for f in inventory.findings] == [22]
    assert inventory.exposed_ports == (22,)


# --- Category: stabilité / déterminisme -------------------------------------


def test_for_asset_is_deterministic() -> None:
    findings = (
        _finding(ip="10.0.0.1", port=22, service="ssh"),
        _finding(ip="10.0.0.1", port=443, service="https"),
        _finding(ip="10.0.0.1", port=3306, service="mysql", exposure=Exposure.INTERNAL_ONLY),
    )
    first = NetworkRisk.for_asset("10.0.0.1", findings)
    second = NetworkRisk.for_asset("10.0.0.1", findings)
    assert first == second
    assert first.exposed_ports == second.exposed_ports
    assert first.exposed_count == second.exposed_count
