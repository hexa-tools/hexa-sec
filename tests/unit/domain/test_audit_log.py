"""Tests for AuditLog (context: evidence — audit trail)."""

from __future__ import annotations

from datetime import datetime

import pytest

from hexa_sec.domain.consent.mandate import MandateId
from hexa_sec.domain.evidence.audit_log import AuditLog, AuditLogId


def test_audit_log_creation() -> None:
    entry = AuditLog(
        entry_id=AuditLogId("log_0001"),
        recorded_at=datetime(2026, 1, 1, 12, 0),
        action="scan_asset",
        actor="operator@hexa.example",
        mandate_id=MandateId("mnd_0001"),
    )
    assert entry.action == "scan_asset"


def test_audit_log_rejects_empty_action() -> None:
    with pytest.raises(ValueError):
        AuditLog(
            entry_id=AuditLogId("log_0002"),
            recorded_at=datetime(2026, 1, 1, 12, 0),
            action="",
            actor="operator@hexa.example",
            mandate_id=None,
        )


def test_audit_log_rejects_empty_actor() -> None:
    with pytest.raises(ValueError):
        AuditLog(
            entry_id=AuditLogId("log_0003"),
            recorded_at=datetime(2026, 1, 1, 12, 0),
            action="scan_asset",
            actor="",
            mandate_id=None,
        )
