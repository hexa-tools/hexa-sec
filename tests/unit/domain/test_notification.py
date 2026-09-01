"""Tests for the Notification aggregate (context: notification, SEC-25)."""

from __future__ import annotations

from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.notification.alert import Alert
from hexa_sec.domain.notification.alert_channel import AlertChannel
from hexa_sec.domain.notification.alert_type import AlertType
from hexa_sec.domain.notification.notification import Notification


def _alert(
    subject: str = "New critical CVE",
    alert_type: AlertType = AlertType.CRITICALCVE,
    severity: Severity = Severity.CRITICAL,
    finding_id: FindingId | None = FindingId("fnd_0001"),
    channel: AlertChannel = AlertChannel.SLACK,
) -> Alert:
    return Alert(
        subject=subject,
        alert_type=alert_type,
        severity=severity,
        channel=channel,
        finding_id=finding_id,
    )


def test_of_consolidates_alerts() -> None:
    alerts = (
        _alert(subject="Secret found", alert_type=AlertType.NEWSECRET, finding_id=FindingId("f1")),
        _alert(
            subject="Exposed port",
            alert_type=AlertType.NEWEXPOSURE,
            severity=Severity.MEDIUM,
            finding_id=FindingId("f2"),
        ),
    )
    notification = Notification.of(alerts)
    assert len(notification.alerts) == 2
    assert notification.critical_count == 1


def test_of_deduplicates_same_key() -> None:
    alerts = (_alert(), _alert())
    notification = Notification.of(alerts)
    assert len(notification.alerts) == 1


def test_of_keeps_higher_severity() -> None:
    medium = _alert(
        alert_type=AlertType.NEWEXPOSURE,
        severity=Severity.MEDIUM,
        finding_id=FindingId("f1"),
    )
    critical = _alert(
        alert_type=AlertType.NEWEXPOSURE,
        severity=Severity.CRITICAL,
        finding_id=FindingId("f1"),
    )
    notification = Notification.of((medium, critical))
    assert len(notification.alerts) == 1
    assert notification.alerts[0].severity is Severity.CRITICAL


def test_of_empty_is_empty() -> None:
    notification = Notification.of(())
    assert notification.alerts == ()
    assert notification.critical_count == 0


def test_of_is_deterministic() -> None:
    alerts = (
        _alert(subject="A", alert_type=AlertType.NEWSECRET, finding_id=FindingId("f1")),
        _alert(subject="B", alert_type=AlertType.NEWEXPOSURE, finding_id=FindingId("f2")),
    )
    first = Notification.of(alerts)
    second = Notification.of(alerts)
    assert first == second
    assert first.critical_count == second.critical_count


def test_of_order_independent() -> None:
    a = _alert(subject="A", alert_type=AlertType.NEWSECRET, finding_id=FindingId("f1"))
    b = _alert(subject="B", alert_type=AlertType.NEWEXPOSURE, finding_id=FindingId("f2"))
    first = Notification.of((a, b))
    second = Notification.of((b, a))
    assert first == second
    assert [alert.subject for alert in first.alerts] == [alert.subject for alert in second.alerts]


# --- Category: concurrence / ordre (clé normalisée + tie-break déterministe) ---
def test_of_dedup_normalizes_padded_finding() -> None:
    alerts = (
        _alert(finding_id=FindingId("fnd_0001")),
        _alert(finding_id=FindingId("fnd_0001  ")),
    )
    notification = Notification.of(alerts)
    assert len(notification.alerts) == 1


def test_of_dedup_same_severity_keeps_deterministic_channel() -> None:
    email = _alert(
        alert_type=AlertType.NEWEXPOSURE,
        severity=Severity.MEDIUM,
        finding_id=FindingId("f1"),
        channel=AlertChannel.EMAIL,
    )
    slack = _alert(
        alert_type=AlertType.NEWEXPOSURE,
        severity=Severity.MEDIUM,
        finding_id=FindingId("f1"),
        channel=AlertChannel.SLACK,
    )
    first = Notification.of((email, slack))
    second = Notification.of((slack, email))
    assert first == second
    assert first.alerts[0].channel.value == "slack"
