"""Tests for Alert (context: notification)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.notification.alert import Alert


def test_alert_creation() -> None:
    alert = Alert(subject="New critical CVE", channel="slack")
    assert alert.channel == "slack"


def test_alert_rejects_empty_subject() -> None:
    with pytest.raises(ValueError):
        Alert(subject="", channel="slack")


def test_alert_rejects_empty_channel() -> None:
    with pytest.raises(ValueError):
        Alert(subject="New critical CVE", channel="")
