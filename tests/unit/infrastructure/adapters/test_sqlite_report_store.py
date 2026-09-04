"""Tests for SqliteReportStore audit trail (secondary adapter)."""

from __future__ import annotations

from pathlib import Path

import pytest

from hexa_sec.application.ports.driven.audit_trail_port import AuditRecord
from hexa_sec.domain.errors import ReportStoreError
from hexa_sec.infrastructure.adapters.secondary.report_store.sqlite_report_store import (
    SqliteReportStore,
)


def _record(tenant_id: str, entry_id: str) -> AuditRecord:
    return AuditRecord(
        tenant_id=tenant_id,
        entry_id=entry_id,
        scan_id="scan_0001",
        mandate_id="mnd_0001",
        action="scan_asset",
        actor="operator@hexa.example",
        image="instrumentisto/nmap@sha256:abc",
        digest="sha256:abc",
        duration_ms=1842,
        recorded_at="2026-01-01T12:00:00",
    )


def test_save_audit_then_load_roundtrips_every_field(tmp_path: Path) -> None:
    store = SqliteReportStore(tmp_path / "reports.db")
    original = _record("tnt_0001", "audit_0001")
    store.save_audit(original)
    entries = store.load_audit("tnt_0001")
    assert len(entries) == 1
    assert entries[0] == original


def test_load_audit_maps_sql_null_columns_to_empty_defaults(tmp_path: Path) -> None:
    store = SqliteReportStore(tmp_path / "reports.db")
    record = store._record("tnt_0001", ("e-1", "2026-01-01", "scan", "op", None, None, None, None, None))
    assert record["mandate_id"] == ""
    assert record["scan_id"] == ""
    assert record["image"] == ""
    assert record["digest"] == ""
    assert record["duration_ms"] == 0


def test_save_audit_translates_infra_error_with_structured_context(tmp_path: Path) -> None:
    store = SqliteReportStore(tmp_path / "reports.db")
    store.save_audit(_record("tnt_0001", "audit_0001"))
    # duplicate primary key -> sqlite3.IntegrityError, translated to ReportStoreError
    with pytest.raises(ReportStoreError) as excinfo:
        store.save_audit(_record("tnt_0001", "audit_0001"))
    assert excinfo.value.message == "audit write failed"
    assert excinfo.value.context == {"tenant_id": "tnt_0001"}


def test_audit_is_tenant_isolated(tmp_path: Path) -> None:
    store = SqliteReportStore(tmp_path / "reports.db")
    store.save_audit(_record("tnt_0001", "audit_0001"))
    # tenant 2 never sees tenant 1's trace (WHERE tenant_id = ?)
    assert store.load_audit("tnt_0002") == []


def test_load_sql_reads_schema(tmp_path: Path) -> None:
    store = SqliteReportStore(tmp_path / "reports.db")
    sql = store._load_sql("schema.sql")
    assert "CREATE TABLE IF NOT EXISTS audit_log" in sql


def test_connect_initializes_schema(tmp_path: Path) -> None:
    store = SqliteReportStore(tmp_path / "reports.db")
    connection = store._connect()
    try:
        cursor = connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        names = {row[0] for row in cursor.fetchall()}
        assert "reports" in names
        assert "audit_log" in names
    finally:
        connection.close()
