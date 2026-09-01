"""CorrelateService — the deterministic product core (US-2, scaffold)."""

from __future__ import annotations

from hexa_sec.application.ports.driving.correlate.correlate_service_port import (
    CorrelateCommand,
    CorrelateResult,
    CorrelateServicePort,
)


class CorrelateService(CorrelateServicePort):
    """Cross findings into correlations (bootstrap stub)."""

    def correlate(self, command: CorrelateCommand) -> CorrelateResult:
        raise NotImplementedError  # pragma: no cover
