"""Tests for FindingKind (context: correlation)."""

from __future__ import annotations

from hexa_sec.domain.correlation.finding_kind import FindingKind


def test_finding_kind_values() -> None:
    assert FindingKind.VULNERABILITY.value == "vulnerability"
    assert FindingKind.SQL_INJECTION.value == "sql_injection"
    assert FindingKind.SECRET.value == "secret"


def test_finding_kind_is_unique() -> None:
    values = [member.value for member in FindingKind]
    assert len(values) == len(set(values))


def test_finding_kind_has_core_kinds() -> None:
    expected = {"VULNERABILITY", "SQL_INJECTION", "SECRET", "EXPOSED_PORT", "NOISE", "COMPLIANCE"}
    assert expected.issubset({member.name for member in FindingKind})
