"""Tests for RecordType (context: dns_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.dns_risk.record_type import RecordType


def test_record_type_values() -> None:
    assert RecordType.A.value == "a"
    assert RecordType.MX.value == "mx"
    assert RecordType.TXT.value == "txt"
    assert RecordType.SOA.value == "soa"


def test_record_type_is_unique() -> None:
    values = [member.value for member in RecordType]
    assert len(values) == len(set(values))


def test_record_type_normalize_accepts_known() -> None:
    assert RecordType.normalize("a") is RecordType.A
    assert RecordType.normalize("AAAA") is RecordType.AAAA
    assert RecordType.normalize("cname") is RecordType.CNAME
    assert RecordType.normalize("ns") is RecordType.NS


def test_record_type_normalize_rejects_unknown() -> None:
    with pytest.raises(ValueError):
        RecordType.normalize("srv")


def test_record_type_normalize_rejects_blank() -> None:
    with pytest.raises(ValueError):
        RecordType.normalize("   ")
