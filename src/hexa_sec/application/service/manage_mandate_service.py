"""ManageMandateService — records legal consent (US-4, scaffold)."""

from __future__ import annotations

from hexa_sec.application.ports.driving.manage_mandate.manage_mandate_service_port import (
    ManageMandateCommand,
    ManageMandateResult,
    ManageMandateServicePort,
)


class ManageMandateService(ManageMandateServicePort):
    """Create and record a signed mandate (bootstrap stub)."""

    def create(self, command: ManageMandateCommand) -> ManageMandateResult:
        raise NotImplementedError  # pragma: no cover
