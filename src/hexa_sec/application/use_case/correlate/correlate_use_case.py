"""CorrelateUseCase — application entry for cross-finding insights (US-2)."""

from __future__ import annotations

from hexa_sec.application.ports.driving.correlate.correlate_service_port import (
    CorrelateCommand,
    CorrelateResult,
    CorrelateServicePort,
)


class CorrelateUseCase(CorrelateServicePort):
    """Depends on the service ABC so it is mockable per test."""

    def __init__(self, service: CorrelateServicePort) -> None:
        self._service = service

    def correlate(self, command: CorrelateCommand) -> CorrelateResult:
        return self._service.correlate(command)
