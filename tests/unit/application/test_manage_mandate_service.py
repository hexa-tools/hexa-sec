"""Tests for ManageMandateService (US-4 orchestration stub)."""

from __future__ import annotations

import pytest

from hexa_sec.application.ports.driving.manage_mandate.manage_mandate_service_port import (
    ManageMandateCommand,
)
from hexa_sec.application.service.manage_mandate_service import ManageMandateService


def test_manage_mandate_service_is_not_implemented() -> None:
    service = ManageMandateService()
    command: ManageMandateCommand = {
        "client": "Acme Corp",
        "targets": ["10.0.0.1"],
        "start_date": "2026-01-01",
        "end_date": "2026-12-31",
        "level": "standard",
    }
    with pytest.raises(NotImplementedError):
        service.create(command)
