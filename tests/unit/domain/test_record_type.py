"""Tests for RecordType (context: dns_risk)."""

from __future__ import annotations

from hexa_sec.domain.dns_risk.record_type import RecordType


def test_record_type_values() -> None:
    assert RecordType.A.value == "a"
    assert RecordType.MX.value == "mx"
    assert RecordType.TXT.value == "txt"
    assert RecordType.SOA.value == "soa"


def test_record_type_is_unique() -> None:
    values = [member.value for member in RecordType]
    assert len(values) == len(set(values))
