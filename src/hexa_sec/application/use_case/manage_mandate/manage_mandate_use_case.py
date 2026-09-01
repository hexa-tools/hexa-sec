"""ManageMandateUseCase — application entry for legal consent (US-4)."""

from __future__ import annotations

from hexa_sec.application.ports.driving.manage_mandate.manage_mandate_service_port import (
    ManageMandateCommand,
    ManageMandateResult,
    ManageMandateServicePort,
)


class ManageMandateUseCase(ManageMandateServicePort):
    """Depends on the service ABC so it is mockable per test."""

    def __init__(self, service: ManageMandateServicePort) -> None:
        self._service = service

    def create(self, command: ManageMandateCommand) -> ManageMandateResult:
        return self._service.create(command)
