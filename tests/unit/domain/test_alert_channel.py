"""Tests for the AlertChannel enum (context: notification, SEC-25)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.notification.alert_channel import AlertChannel


def test_alert_channel_members() -> None:
    assert AlertChannel.SLACK.value == "slack"
    assert AlertChannel.EMAIL.value == "email"
    assert AlertChannel.WEBHOOK.value == "webhook"


def test_alert_channel_unique_values() -> None:
    values = [member.value for member in AlertChannel]
    assert len(values) == len(set(values))


def test_alert_channel_normalize_accepts_known() -> None:
    assert AlertChannel.normalize("slack") is AlertChannel.SLACK
    assert AlertChannel.normalize("EMAIL") is AlertChannel.EMAIL
    assert AlertChannel.normalize("webhook") is AlertChannel.WEBHOOK


def test_alert_channel_normalize_rejects_unknown() -> None:
    with pytest.raises(ValueError, match="unknown alert channel: telegram"):
        AlertChannel.normalize("telegram")


def test_alert_channel_normalize_rejects_blank() -> None:
    with pytest.raises(ValueError, match="unknown alert channel:"):
        AlertChannel.normalize("   ")
