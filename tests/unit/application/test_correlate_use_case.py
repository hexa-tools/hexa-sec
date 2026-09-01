"""Tests for CorrelateUseCase (US-2)."""

from __future__ import annotations

import pytest

from hexa_sec.application.ports.driving.correlate.correlate_service_port import CorrelateCommand
from hexa_sec.application.service.correlate_service import CorrelateService
from hexa_sec.application.use_case.correlate.correlate_use_case import CorrelateUseCase


def test_correlate_use_case_delegates_to_service() -> None:
    use_case = CorrelateUseCase(CorrelateService())
    command: CorrelateCommand = {"scan_id": "scan_0001"}
    with pytest.raises(NotImplementedError):
        use_case.correlate(command)
