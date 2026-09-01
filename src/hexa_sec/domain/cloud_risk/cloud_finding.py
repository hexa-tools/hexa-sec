"""CloudFinding — a cloud misconfiguration exposure (context: cloud_risk)."""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.cloud_risk.cloud_resource import CloudResource
from hexa_sec.domain.finding.severity import Severity


@dataclass(frozen=True)
class CloudFinding:
    """A cloud resource misconfiguration."""

    resource: CloudResource
    issue: str
    severity: Severity = Severity.MEDIUM

    def __post_init__(self) -> None:
        if not isinstance(self.resource, CloudResource):
            raise ValueError("cloud finding resource must be a CloudResource")
        if not self.issue.strip():
            raise ValueError("cloud finding issue cannot be empty")
        if not isinstance(self.severity, Severity):
            raise ValueError("cloud finding severity must be a Severity")
        object.__setattr__(self, "issue", self.issue.strip())

    def exposed(self) -> bool:
        return self.resource.is_public()
