"""Tests for AuditConsent (context: consent)."""

from __future__ import annotations

from datetime import datetime

import pytest

from hexa_sec.domain.consent.audit_consent import AuditConsent
from hexa_sec.domain.consent.mandate import MandateId


def test_audit_consent_creation() -> None:
    entry = AuditConsent(
        mandate_id=MandateId("mnd_0001"),
        recorded_at=datetime(2026, 1, 1, 12, 0),
        actor="consultant@hexa.example",
        decision="approved",
    )
    assert entry.decision == "approved"


def test_audit_consent_rejects_empty_actor() -> None:
    with pytest.raises(ValueError):
        AuditConsent(
            mandate_id=MandateId("mnd_0001"),
            recorded_at=datetime(2026, 1, 1, 12, 0),
            actor="",
            decision="approved",
        )


def test_audit_consent_rejects_empty_decision() -> None:
    with pytest.raises(ValueError):
        AuditConsent(
            mandate_id=MandateId("mnd_0001"),
            recorded_at=datetime(2026, 1, 1, 12, 0),
            actor="consultant@hexa.example",
            decision="",
        )
