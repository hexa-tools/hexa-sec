"""Tests for ManageMandateUseCase (US-4)."""

from __future__ import annotations

from hexa_sec.application.ports.driving.manage_mandate.manage_mandate_service_port import (
    ManageMandateCommand,
    ManageMandateServicePort,
)
from hexa_sec.application.use_case.manage_mandate.manage_mandate_use_case import (
    ManageMandateUseCase,
)


class _Stub(ManageMandateServicePort):
    def create(self, command: ManageMandateCommand) -> dict[str, str]:
        return {"mandate_id": "mnd_0001", "level": command["level"]}


def test_manage_mandate_use_case_delegates_to_service() -> None:
    use_case = ManageMandateUseCase(_Stub())
    command: ManageMandateCommand = {
        "client": "Acme",
        "targets": ["10.0.0.1"],
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "level": "standard",
        "signature": "REF-2026-0001",
        "actor": "operator",
        "tenant_id": "tnt_0001",
    }
    result = use_case.create(command)
    assert result["mandate_id"] == "mnd_0001"
    assert result["level"] == "standard"
