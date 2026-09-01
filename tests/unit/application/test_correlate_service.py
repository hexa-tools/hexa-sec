"""Tests for CorrelateService (US-2 orchestration stub)."""

from __future__ import annotations

import pytest

from hexa_sec.application.ports.driving.correlate.correlate_service_port import CorrelateCommand
from hexa_sec.application.service.correlate_service import CorrelateService


def test_correlate_service_is_not_implemented() -> None:
    service = CorrelateService()
    command: CorrelateCommand = {"scan_id": "scan_0001"}
    with pytest.raises(NotImplementedError):
        service.correlate(command)
