"""Tests for Alert (context: notification, SEC-25)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.notification.alert import Alert
from hexa_sec.domain.notification.alert_channel import AlertChannel
from hexa_sec.domain.notification.alert_type import AlertType


def _alert(
    subject: str = "New critical CVE",
    alert_type: AlertType = AlertType.CRITICALCVE,
    severity: Severity = Severity.CRITICAL,
    channel: AlertChannel = AlertChannel.SLACK,
    finding_id: FindingId | None = FindingId("fnd_0001"),
) -> Alert:
    return Alert(
        subject=subject,
        alert_type=alert_type,
        severity=severity,
        channel=channel,
        finding_id=finding_id,
    )


def test_alert_creation() -> None:
    alert = _alert()
    assert alert.subject == "New critical CVE"
    assert alert.alert_type is AlertType.CRITICALCVE
    assert alert.severity is Severity.CRITICAL
    assert alert.channel is AlertChannel.SLACK
    assert alert.finding_id == FindingId("fnd_0001")


def test_alert_normalizes_subject() -> None:
    assert _alert(subject="  New CVE  ").subject == "New CVE"


def test_alert_rejects_empty_subject() -> None:
    with pytest.raises(ValueError):
        _alert(subject="")


def test_alert_rejects_blank_subject() -> None:
    with pytest.raises(ValueError):
        _alert(subject="   ")


def test_alert_rejects_non_type() -> None:
    with pytest.raises(ValueError):
        _alert(alert_type="critical_cve")  # type: ignore[arg-type]


def test_alert_rejects_non_severity() -> None:
    with pytest.raises(ValueError):
        _alert(severity="critical")  # type: ignore[arg-type]


def test_alert_rejects_non_channel() -> None:
    with pytest.raises(ValueError):
        _alert(channel="slack")  # type: ignore[arg-type]


def test_alert_rejects_critical_without_finding() -> None:
    with pytest.raises(ValueError):
        _alert(finding_id=None)
    with pytest.raises(ValueError):
        _alert(finding_id=FindingId(""))


def test_alert_accepts_critical_with_finding() -> None:
    assert _alert(finding_id=FindingId("fnd_1")).finding_id == FindingId("fnd_1")


def test_alert_accepts_non_critical_without_finding() -> None:
    alert = _alert(
        alert_type=AlertType.NEWEXPOSURE,
        severity=Severity.MEDIUM,
        finding_id=None,
    )
    assert alert.finding_id is None
