"""Tests for the AccessRisk enum (context: identity_risk, SEC-19)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.identity_risk.access_risk import AccessRisk


def test_access_risk_members() -> None:
    assert AccessRisk.ORPHAN.value == "orphan"
    assert AccessRisk.EXCESSIVE.value == "excessive"
    assert AccessRisk.PRIVILEGED.value == "privileged"
    assert AccessRisk.SERVICE.value == "service"
    assert AccessRisk.NORMAL.value == "normal"


def test_access_risk_unique_values() -> None:
    values = [member.value for member in AccessRisk]
    assert len(values) == len(set(values))


def test_access_risk_normalize_accepts_known_values() -> None:
    assert AccessRisk.normalize("orphan") is AccessRisk.ORPHAN
    assert AccessRisk.normalize("EXCESSIVE") is AccessRisk.EXCESSIVE
    assert AccessRisk.normalize("privileged") is AccessRisk.PRIVILEGED
    assert AccessRisk.normalize("service") is AccessRisk.SERVICE
    assert AccessRisk.normalize("normal") is AccessRisk.NORMAL


def test_access_risk_normalize_rejects_unknown() -> None:
    with pytest.raises(ValueError):
        AccessRisk.normalize("domain_admin")


def test_access_risk_normalize_rejects_blank() -> None:
    with pytest.raises(ValueError):
        AccessRisk.normalize("   ")


def test_access_risk_min_severity_privileged_at_least_high() -> None:
    assert AccessRisk.PRIVILEGED.min_severity().rank >= Severity.HIGH.rank


def test_access_risk_min_severity_others_no_floor() -> None:
    assert AccessRisk.ORPHAN.min_severity() is Severity.LOW
    assert AccessRisk.EXCESSIVE.min_severity() is Severity.LOW
    assert AccessRisk.SERVICE.min_severity() is Severity.LOW
    assert AccessRisk.NORMAL.min_severity() is Severity.LOW
