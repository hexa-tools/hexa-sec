"""ManageMandateService — records legal consent (US-4).

Creates a versioned :class:`Mandate` (the Godfrain gate, never mutated —
modification is a new mandate), and traces the consent decision in the audit
trail (append-only). Never try/catch (R6) — the domain invariants raise.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import uuid4

from hexa_sec.application.ports.driven.audit_trail_port import AuditRecord, AuditTrailPort
from hexa_sec.application.ports.driving.manage_mandate.manage_mandate_service_port import (
    ManageMandateCommand,
    ManageMandateResult,
    ManageMandateServicePort,
)
from hexa_sec.domain.consent.mandate import Mandate, MandateId, MandateLevel


class ManageMandateService(ManageMandateServicePort):
    """Create and record a signed mandate."""

    def __init__(self, audit_trail: AuditTrailPort | None = None) -> None:
        self._audit_trail = audit_trail

    def create(self, command: ManageMandateCommand) -> ManageMandateResult:
        mandate_id = MandateId(f"mnd_{uuid4().hex}")
        mandate = Mandate(
            mandate_id=mandate_id,
            client=command["client"],
            targets=tuple(command["targets"]),
            start_date=date.fromisoformat(command["start_date"]),
            end_date=date.fromisoformat(command["end_date"]),
            level=MandateLevel(command["level"]),
            signature=command["signature"],
        )
        self._trace(mandate, command)
        return ManageMandateResult(
            mandate_id=mandate.mandate_id.value,
            level=mandate.level.value,
        )

    def _trace(self, mandate: Mandate, command: ManageMandateCommand) -> None:
        if self._audit_trail is None:
            return
        recorded_at = datetime.now(UTC)
        self._audit_trail.save_audit(
            AuditRecord(
                tenant_id=command["tenant_id"],
                entry_id=mandate.mandate_id.value,
                scan_id="",
                mandate_id=mandate.mandate_id.value,
                action="consent",
                actor=command["actor"],
                image=command["client"],
                digest="",
                duration_ms=0,
                recorded_at=recorded_at.isoformat(),
            )
        )
