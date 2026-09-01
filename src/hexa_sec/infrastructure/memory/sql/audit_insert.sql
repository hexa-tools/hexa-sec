-- INSERT an audit trail entry. Loaded by the report_store adapter; never
-- written inline in Python. Values are bound with ? placeholders.
INSERT INTO audit_log (entry_id, recorded_at, action, actor, mandate_id, scan_id, image, digest, duration_ms, tenant_id)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
