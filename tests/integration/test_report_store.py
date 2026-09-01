"""Integration — SqliteReportStore against a real local SQLite file.

No network, no scanner, no keys. Just a real backend (SQLite) to verify the
adapter wires the schema correctly.
"""

from __future__ import annotations

import pytest
from pathlib import Path

from hexa_sec.adapters.secondary.report_store.sqlite_report_store import SqliteReportStore


@pytest.mark.integration
def test_report_store_creates_schema_and_connects(tmp_path: Path) -> None:
    store = SqliteReportStore(tmp_path / "reports.db")
    connection = store._connect()
    try:
        cursor = connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        assert {"reports", "audit_log"}.issubset(tables)
    finally:
        connection.close()


@pytest.mark.integration
def test_tenant_isolation_columns_present(tmp_path: Path) -> None:
    store = SqliteReportStore(tmp_path / "reports.db")
    connection = store._connect()
    try:
        cursor = connection.execute("PRAGMA table_info(reports)")
        columns = {row[1] for row in cursor.fetchall()}
        assert "tenant_id" in columns
    finally:
        connection.close()
