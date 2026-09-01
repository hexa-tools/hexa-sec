"""Tests for the DnsRisk aggregate (context: dns_risk)."""

from __future__ import annotations

from hexa_sec.domain.dns_risk.dns_finding import DnsFinding
from hexa_sec.domain.dns_risk.dns_record import DnsRecord
from hexa_sec.domain.dns_risk.dns_risk import DnsRisk
from hexa_sec.domain.dns_risk.record_type import RecordType
from hexa_sec.domain.dns_risk.subdomain import Subdomain


def _finding(
    domain: str,
    subdomains: tuple[Subdomain, ...] = (),
    zone_transfer: bool = False,
) -> DnsFinding:
    return DnsFinding(domain=domain, subdomains=subdomains, zone_transfer=zone_transfer)


def test_of_consolidates_findings() -> None:
    findings = (
        _finding("acme.example", (Subdomain("admin.acme.example", resolved=True),)),
        _finding("corp.example"),
    )
    risk = DnsRisk.of(findings)
    assert len(risk.findings) == 2
    assert risk.exposed_count == 1


def test_of_deduplicates_same_domain() -> None:
    findings = (
        _finding("acme.example", (Subdomain("admin.acme.example", resolved=True),)),
        _finding("acme.example"),
    )
    risk = DnsRisk.of(findings)
    assert len(risk.findings) == 1
    assert risk.findings[0].exposed() is True


def test_of_exposed_domains() -> None:
    findings = (
        _finding("acme.example", (Subdomain("admin.acme.example", resolved=True),)),
        _finding("corp.example"),
    )
    risk = DnsRisk.of(findings)
    assert risk.exposed_domains() == ("acme.example",)
    assert risk.exposed_count == 1


def test_of_zone_transfer_count() -> None:
    findings = (
        _finding("acme.example", zone_transfer=True),
        _finding("corp.example"),
    )
    risk = DnsRisk.of(findings)
    assert risk.zone_transfer_count == 1


def test_of_empty_is_empty() -> None:
    risk = DnsRisk.of(())
    assert risk.findings == ()
    assert risk.exposed_count == 0
    assert risk.exposed_domains() == ()


def test_of_is_deterministic() -> None:
    findings = (
        _finding("acme.example", (Subdomain("a.acme.example", resolved=True),)),
        _finding("corp.example"),
    )
    first = DnsRisk.of(findings)
    second = DnsRisk.of(findings)
    assert first == second
    assert first.exposed_count == second.exposed_count


def test_of_order_independent() -> None:
    a = _finding("acme.example", (Subdomain("a.acme.example", resolved=True),))
    b = _finding("corp.example")
    first = DnsRisk.of((a, b))
    second = DnsRisk.of((b, a))
    assert first == second
    assert [finding.domain for finding in first.findings] == [
        finding.domain for finding in second.findings
    ]
