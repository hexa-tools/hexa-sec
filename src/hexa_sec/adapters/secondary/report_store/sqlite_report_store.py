"""SqliteReportStore — report/audit persistence (secondary adapter).

SQL is never inline in Python: it is loaded from ``infrastructure/memory/sql``.
Audit entries are tenant-scoped (``WHERE tenant_id = ?``), so one tenant never
reads another's trace.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from hexa_sec.application.ports.driven.audit_trail_port import AuditRecord, AuditTrailPort
from hexa_sec.application.ports.driven.report_store_port import ReportRecord, ReportStorePort
from hexa_sec.domain.errors import ReportStoreError

SQL_DIR = Path(__file__).resolve().parents[3] / "infrastructure" / "memory" / "sql"


class SqliteReportStore(ReportStorePort, AuditTrailPort):
    """Persist reports and the audit trail via SQLite."""

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

    def save_audit(self, record: AuditRecord) -> None:
        try:
            with self._connect() as connection:
                connection.execute(
                    self._load_sql("audit_insert.sql"),
                    (
                        record["entry_id"],
                        record["recorded_at"],
                        record["action"],
                        record["actor"],
                        record["mandate_id"],
                        record["scan_id"],
                        record["image"],
                        record["digest"],
                        record["duration_ms"],
                        record["tenant_id"],
                    ),
                )
        except sqlite3.Error as error:
            # infra exceptions never escape a secondary adapter
            raise ReportStoreError(
                "audit write failed", {"tenant_id": record["tenant_id"]}
            ) from error

    def load_audit(self, tenant_id: str) -> list[AuditRecord]:
        with self._connect() as connection:
            rows = connection.execute(self._load_sql("audit_select.sql"), (tenant_id,)).fetchall()
        return [self._record(tenant_id, row) for row in rows]

    @staticmethod
    def _record(tenant_id: str, row: tuple[object, ...]) -> AuditRecord:
        return AuditRecord(
            tenant_id=tenant_id,
            entry_id=str(row[0]),
            recorded_at=str(row[1]),
            action=str(row[2]),
            actor=str(row[3]),
            mandate_id=_text(row[4]),
            scan_id=_text(row[5]),
            image=_text(row[6]),
            digest=_text(row[7]),
            duration_ms=_int(row[8]),
        )


def _text(value: object) -> str:
    return str(value) if value is not None else ""


def _int(value: object) -> int:
    if isinstance(value, (int, float, str)):
        return int(value)
    return 0
