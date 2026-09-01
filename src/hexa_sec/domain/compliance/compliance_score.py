"""ComplianceScore — a 0..100 score per framework (context: compliance)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from hexa_sec.domain.compliance.compliance_scope import ComplianceScope


class ComplianceLevel(Enum):
    """Interpreted compliance posture."""

    COMPLIANT = "compliant"
    ADEQUATE = "adequate"
    NON_COMPLIANT = "non_compliant"


@dataclass(frozen=True)
class ComplianceScore:
    """How well a framework is satisfied."""

    scope: ComplianceScope
    value: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 100.0:
            raise ValueError("compliance score must be between 0 and 100")

    def level(self) -> ComplianceLevel:
        if self.value >= 85.0:
            return ComplianceLevel.COMPLIANT
        if self.value >= 60.0:
            return ComplianceLevel.ADEQUATE
        return ComplianceLevel.NON_COMPLIANT
