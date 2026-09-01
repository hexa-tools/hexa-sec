"""SqliteReportStore — report/audit persistence (secondary adapter).

SQL is never inline in Python: it is loaded from ``infrastructure/memory/sql``.
Phase 4 wires ``save``/``load`` against that schema.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from hexa_sec.application.ports.driven.report_store_port import ReportRecord, ReportStorePort

SQL_DIR = Path(__file__).resolve().parents[3] / "infrastructure" / "memory" / "sql"


class SqliteReportStore(ReportStorePort):
    """Persist reports via SQLite, reading statements from .sql files."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def _load_sql(self, filename: str) -> str:
        return (SQL_DIR / filename).read_text(encoding="utf-8")

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path)
        connection.executescript(self._load_sql("schema.sql"))
        return connection

    def save(self, record: ReportRecord) -> None:
        raise NotImplementedError  # pragma: no cover

    def load(self, report_id: str) -> ReportRecord | None:
        raise NotImplementedError  # pragma: no cover
