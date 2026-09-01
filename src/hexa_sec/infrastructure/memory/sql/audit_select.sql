-- SELECT audit trail entries for one tenant. Tenant filter is mandatory.
SELECT entry_id, recorded_at, action, actor, mandate_id, scan_id, image, digest, duration_ms, tenant_id
FROM audit_log
WHERE tenant_id = ?
ORDER BY recorded_at;
