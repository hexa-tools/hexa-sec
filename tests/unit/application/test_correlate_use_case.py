"""Tests for CorrelateUseCase (US-2)."""

from __future__ import annotations

from hexa_sec.application.ports.driving.correlate.correlate_service_port import (
    CorrelateCommand,
    CorrelateServicePort,
)
from hexa_sec.application.use_case.correlate.correlate_use_case import CorrelateUseCase


class _Stub(CorrelateServicePort):
    def correlate(self, command: CorrelateCommand) -> dict[str, object]:
        return {"scan_id": command["scan_id"], "correlations": []}


def test_correlate_use_case_delegates_to_service() -> None:
    use_case = CorrelateUseCase(_Stub())
    command: CorrelateCommand = {
        "scan_id": "scan_0001",
        "signals": (),
        "previous": (),
        "asset_criticalities": {},
        "exposure_open_ports": 3,
        "noise_count": 10,
    }
    result = use_case.correlate(command)
    assert result["scan_id"] == "scan_0001"
    assert result["correlations"] == []
