"""Tests for the AlertType enum (context: notification, SEC-25)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.notification.alert_type import AlertType


def test_alert_type_members() -> None:
    assert AlertType.NEWSECRET.value == "new_secret"
    assert AlertType.CRITICALCVE.value == "critical_cve"
    assert AlertType.NEWEXPOSURE.value == "new_exposure"
    assert AlertType.COMPLIANCEGAP.value == "compliance_gap"
    assert AlertType.FIX_RESOLVED.value == "fix_resolved"


def test_alert_type_unique_values() -> None:
    values = [member.value for member in AlertType]
    assert len(values) == len(set(values))


def test_alert_type_normalize_accepts_known() -> None:
    assert AlertType.normalize("new_secret") is AlertType.NEWSECRET
    assert AlertType.normalize("critical cve") is AlertType.CRITICALCVE
    assert AlertType.normalize("NEWSECRET") is AlertType.NEWSECRET
    assert AlertType.normalize("fix-resolved") is AlertType.FIX_RESOLVED


def test_alert_type_normalize_rejects_unknown() -> None:
    with pytest.raises(ValueError):
        AlertType.normalize("quota_exceeded")


def test_alert_type_normalize_rejects_blank() -> None:
    with pytest.raises(ValueError):
        AlertType.normalize("   ")
