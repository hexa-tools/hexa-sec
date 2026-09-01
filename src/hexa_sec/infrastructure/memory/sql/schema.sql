-- schema.sql — hexa-sec persistence (reports + audit trail).
-- Loaded by the report_store adapter. No SQL is ever inline in Python.
-- Every multi-tenant query carries WHERE tenant_id = ?.

CREATE TABLE IF NOT EXISTS reports (
    id          TEXT PRIMARY KEY,
    tenant_id   TEXT NOT NULL,
    title       TEXT NOT NULL,
    content     TEXT NOT NULL,
    score       REAL,
    created_at  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_reports_tenant ON reports (tenant_id);

CREATE TABLE IF NOT EXISTS audit_log (
    entry_id    TEXT PRIMARY KEY,
    recorded_at TEXT NOT NULL,
    action      TEXT NOT NULL,
    actor       TEXT NOT NULL,
    mandate_id  TEXT,
    scan_id     TEXT,
    image       TEXT,
    digest      TEXT,
    duration_ms INTEGER,
    tenant_id   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_audit_tenant ON audit_log (tenant_id);
