"""CorrelateService — the deterministic product core (US-2).

A thin orchestrator over the pure domain checker: it builds the deterministic
:class:`CorrelationContext` from the command and lets the domain ``correlate()``
do the crossing. No I/O, no LLM, no try/catch (R6) — the domain raises nothing
here, and the result is fully reproducible.
"""

from __future__ import annotations

from hexa_sec.application.ports.driving.correlate.correlate_service_port import (
    CorrelateCommand,
    CorrelateResult,
    CorrelateServicePort,
    CorrelationRecord,
)
from hexa_sec.domain.correlation.correlation import Correlation
from hexa_sec.domain.correlation.correlation_checker import correlate as correlate_domain
from hexa_sec.domain.correlation.correlation_context import CorrelationContext


class CorrelateService(CorrelateServicePort):
    """Cross findings into correlations, deterministically."""

    def correlate(self, command: CorrelateCommand) -> CorrelateResult:
        context = CorrelationContext(
            exposure_open_ports=command["exposure_open_ports"],
            noise_count=command["noise_count"],
            asset_criticalities=dict(command["asset_criticalities"]),
            previous=tuple(command["previous"]),
        )
        correlations = correlate_domain(tuple(command["signals"]), context)
        return CorrelateResult(
            scan_id=command["scan_id"],
            correlations=[self._to_record(correlation) for correlation in correlations],
        )

    @staticmethod
    def _to_record(correlation: Correlation) -> CorrelationRecord:
        return CorrelationRecord(
            type=correlation.type.value,
            reason=correlation.reason,
            findings=[finding.value for finding in correlation.findings],
            impact=correlation.impact.level().value,
        )
