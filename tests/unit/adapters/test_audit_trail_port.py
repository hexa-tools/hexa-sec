"""Tests for the AuditTrailPort contract (traceability)."""

from __future__ import annotations

import inspect

from hexa_sec.application.ports.driven.audit_trail_port import AuditRecord, AuditTrailPort


def test_audit_trail_port_is_abstract() -> None:
    assert inspect.isabstract(AuditTrailPort) is True


def test_audit_record_typeddict_requires_tenant() -> None:
    record: AuditRecord = {
        "tenant_id": "tnt_0001",
        "entry_id": "audit_0001",
        "scan_id": "scan_0001",
        "mandate_id": "mnd_0001",
        "action": "scan_asset",
        "actor": "operator@hexa.example",
        "image": "instrumentisto/nmap@sha256:abc",
        "digest": "sha256:abc",
        "duration_ms": 1842,
        "recorded_at": "2026-01-01T12:00:00",
    }
    assert record["image"].endswith("@sha256:abc")
    assert record["tenant_id"] == "tnt_0001"
