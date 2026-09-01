"""ComplianceFinding — the deterministic finding→framework link (context: compliance).

This is the piece that ties a finding to the frameworks it fails. A finding is
never attached to a framework by chance: the scope is required and the anchor is
an explicit ``FindingId``. Unknown/blank anchors are rejected — no speculation.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.compliance.compliance_scope import ComplianceScope
from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.finding.severity import Severity


@dataclass(frozen=True)
class ComplianceFinding:
    """A finding linked to an accountability framework."""

    finding_id: FindingId
    scope: ComplianceScope
    impact: Severity

    def __post_init__(self) -> None:
        if not isinstance(self.finding_id, FindingId) or not self.finding_id.value.strip():
            raise ValueError("compliance finding requires a non-empty finding id")
        if not isinstance(self.scope, ComplianceScope):
            raise ValueError("compliance finding scope must be a ComplianceScope")
        if not isinstance(self.impact, Severity):
            raise ValueError("compliance finding impact must be a Severity")
