"""Tests for ManageMandateUseCase (US-4)."""

from __future__ import annotations

import pytest

from hexa_sec.application.ports.driving.manage_mandate.manage_mandate_service_port import (
    ManageMandateCommand,
)
from hexa_sec.application.service.manage_mandate_service import ManageMandateService
from hexa_sec.application.use_case.manage_mandate.manage_mandate_use_case import ManageMandateUseCase


def test_manage_mandate_use_case_delegates_to_service() -> None:
    use_case = ManageMandateUseCase(ManageMandateService())
    command: ManageMandateCommand = {
        "client": "Acme",
        "targets": ["10.0.0.1"],
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "level": "standard",
    }
    with pytest.raises(NotImplementedError):
        use_case.create(command)
