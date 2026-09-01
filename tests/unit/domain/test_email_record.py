"""Tests for EmailRecord (context: email_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.email_risk.email_record import EmailRecord


def test_email_record_creation() -> None:
    record = EmailRecord(domain="acme.example", spf="v=spf1 -all", dkim="v=DKIM1; k=rsa")
    assert record.domain == "acme.example"
    assert record.dkim.startswith("v=DKIM1")


def test_email_record_defaults() -> None:
    record = EmailRecord(domain="acme.example")
    assert record.spf == ""
    assert record.dkim == ""


def test_email_record_rejects_empty_domain() -> None:
    with pytest.raises(ValueError):
        EmailRecord(domain="")
