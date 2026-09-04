"""Tests for Ioc and IocType (context: threat_intel, SEC-20)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.threat_intel.ioc import Ioc, IocType


def test_ioc_type_members() -> None:
    assert IocType.IP.value == "ip"
    assert IocType.DOMAIN.value == "domain"
    assert IocType.HASH.value == "hash"
    assert IocType.URL.value == "url"


def test_ioc_type_unique_values() -> None:
    values = [member.value for member in IocType]
    assert len(values) == len(set(values))


def test_ioc_type_normalize_accepts_known() -> None:
    assert IocType.normalize("ip") is IocType.IP
    assert IocType.normalize("DOMAIN") is IocType.DOMAIN
    assert IocType.normalize("hash") is IocType.HASH


def test_ioc_type_normalize_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="unknown ioc type: email"):
        IocType.normalize("email")


def test_ioc_type_normalize_rejects_blank() -> None:
    with pytest.raises(ValueError, match="unknown ioc type:"):
        IocType.normalize("   ")


def test_ioc_creation() -> None:
    ioc = Ioc("203.0.113.9", IocType.IP)
    assert ioc.value == "203.0.113.9"
    assert ioc.ioc_type is IocType.IP


def test_ioc_trims_value() -> None:
    assert Ioc("  evil.example  ", IocType.DOMAIN).value == "evil.example"


def test_ioc_rejects_empty_value() -> None:
    with pytest.raises(ValueError):
        Ioc("", IocType.IP)


def test_ioc_rejects_blank_value() -> None:
    with pytest.raises(ValueError):
        Ioc("   ", IocType.IP)


def test_ioc_rejects_non_type() -> None:
    with pytest.raises(ValueError):
        Ioc("203.0.113.9", "ip")
