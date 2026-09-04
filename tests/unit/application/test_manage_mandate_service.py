"""Tests for ManageMandateService (US-4 legal consent)."""

from __future__ import annotations

import pytest

from hexa_sec.application.ports.driven.audit_trail_port import AuditRecord, AuditTrailPort
from hexa_sec.application.ports.driving.manage_mandate.manage_mandate_service_port import (
    ManageMandateCommand,
)
from hexa_sec.application.service.manage_mandate_service import ManageMandateService


class _Audit(AuditTrailPort):
    def __init__(self) -> None:
        self.records: list[AuditRecord] = []

    def save_audit(self, record: AuditRecord) -> None:
        self.records.append(record)

    def load_audit(self, tenant_id: str) -> list[AuditRecord]:
        return self.records


def _command(**overrides: object) -> ManageMandateCommand:
    defaults: dict[str, object] = {
        "client": "Acme Corp",
        "targets": ["10.0.0.1"],
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "level": "standard",
        "signature": "REF-2026-0001",
        "actor": "operator",
        "tenant_id": "tnt_0001",
    }
    defaults.update(overrides)
    return ManageMandateCommand(**defaults)  # type: ignore[arg-type]


def test_create_valid_mandate_and_trace() -> None:
    audit = _Audit()
    service = ManageMandateService(audit_trail=audit)
    result = service.create(_command())
    assert result["mandate_id"].startswith("mnd_")
    assert result["level"] == "standard"
    assert len(audit.records) == 1
    record = audit.records[0]
    assert record["mandate_id"] == result["mandate_id"]
    assert record["action"] == "consent"
    assert record["actor"] == "operator"
    assert record["tenant_id"] == "tnt_0001"


def test_create_rejects_empty_signature() -> None:
    with pytest.raises(ValueError):
        ManageMandateService().create(_command(signature=""))


def test_create_rejects_empty_targets() -> None:
    with pytest.raises(ValueError):
        ManageMandateService().create(_command(targets=[]))


def test_create_rejects_end_before_start() -> None:
    with pytest.raises(ValueError):
        ManageMandateService().create(
            _command(start_date="2026-12-31", end_date="2026-01-01")
        )


def test_create_without_audit_trail_still_returns() -> None:
    result = ManageMandateService().create(_command())
    assert result["mandate_id"].startswith("mnd_")
    assert result["level"] == "standard"
