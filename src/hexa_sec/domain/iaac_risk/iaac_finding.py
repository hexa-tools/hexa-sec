"""IaacFinding — a risky infrastructure-as-code resource (context: iaac_risk, SEC-17).

An adapter (checkov) translates a scanner hit into an IaacFinding: the
ResourceType, the IaCFileName (path), the Severity and the evidence. The
severity must respect the resource type floor — a public bucket can never be
LOW — and the evidence is mandatory (no invented misconfiguration).
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.iaac_risk.ia_c_file_name import IaCFileName
from hexa_sec.domain.iaac_risk.resource_type import ResourceType


@dataclass(frozen=True)
class IaacFinding:
    """A single risky IaC resource."""

    resource_type: ResourceType
    path: IaCFileName
    severity: Severity
    evidence: str

    def __post_init__(self) -> None:
        if not isinstance(self.resource_type, ResourceType):
            raise ValueError("iaac finding resource_type must be a ResourceType")
        if not isinstance(self.path, IaCFileName):
            raise ValueError("iaac finding path must be an IaCFileName")
        if not isinstance(self.severity, Severity):
            raise ValueError("iaac finding severity must be a Severity")
        if not self.evidence or not self.evidence.strip():
            raise ValueError("iaac finding requires evidence (proof)")
        if self.severity.rank < self.resource_type.min_severity().rank:
            raise ValueError(
                f"iaac finding severity too low for {self.resource_type.value} "
                "(public resource must be at least HIGH)"
            )
