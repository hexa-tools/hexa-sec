"""Tests for DnsRecord (context: dns_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.dns_risk.dns_record import DnsRecord
from hexa_sec.domain.dns_risk.record_type import RecordType


def test_dns_record_creation() -> None:
    record = DnsRecord(name="www.acme.example", record_type=RecordType.A, value="10.0.0.1")
    assert record.value == "10.0.0.1"
    assert record.record_type is RecordType.A


def test_dns_record_rejects_empty_name() -> None:
    with pytest.raises(ValueError):
        DnsRecord(name="", record_type=RecordType.A, value="10.0.0.1")


def test_dns_record_rejects_empty_value() -> None:
    with pytest.raises(ValueError):
        DnsRecord(name="www.acme.example", record_type=RecordType.A, value="")


def test_dns_record_rejects_non_type() -> None:
    with pytest.raises(ValueError):
        DnsRecord(name="www.acme.example", record_type="a", value="10.0.0.1")  # type: ignore[arg-type]
