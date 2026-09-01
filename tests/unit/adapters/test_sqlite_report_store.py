"""Tests for SqliteReportStore (secondary adapter)."""

from __future__ import annotations

from pathlib import Path

from hexa_sec.adapters.secondary.report_store.sqlite_report_store import SqliteReportStore


def test_load_sql_reads_schema(tmp_path: Path) -> None:
    store = SqliteReportStore(tmp_path / "reports.db")
    sql = store._load_sql("schema.sql")
    assert "CREATE TABLE IF NOT EXISTS reports" in sql


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
