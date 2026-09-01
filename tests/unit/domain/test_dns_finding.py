"""Tests for DnsFinding (context: dns_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.dns_risk.dns_finding import DnsFinding
from hexa_sec.domain.dns_risk.dns_record import DnsRecord
from hexa_sec.domain.dns_risk.record_type import RecordType
from hexa_sec.domain.dns_risk.subdomain import Subdomain


def test_dns_finding_creation() -> None:
    record = DnsRecord(name="www.acme.example", record_type=RecordType.A, value="10.0.0.1")
    finding = DnsFinding(domain="acme.example", records=(record,))
    assert finding.domain == "acme.example"
    assert finding.records == (record,)


def test_dns_finding_zone_transfer() -> None:
    finding = DnsFinding(domain="acme.example", zone_transfer=True)
    assert finding.has_zone_transfer() is True


def test_dns_finding_exposed_subdomain() -> None:
    finding = DnsFinding(
        domain="acme.example",
        subdomains=(Subdomain(name="admin.acme.example", resolved=True),),
    )
    assert finding.exposed() is True


def test_dns_finding_not_exposed() -> None:
    finding = DnsFinding(domain="acme.example")
    assert finding.exposed() is False


def test_dns_finding_rejects_empty_domain() -> None:
    with pytest.raises(ValueError):
        DnsFinding(domain="")
