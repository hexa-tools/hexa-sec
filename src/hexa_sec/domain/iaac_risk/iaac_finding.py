"""IaacFinding — a risky infrastructure-as-code resource (context: iaac_risk)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IaacFinding:
    """A terraform/helm/cloud-config risk."""

    resource_type: str
    path: str

    def __post_init__(self) -> None:
        if not self.resource_type:
            raise ValueError("iaac finding resource type cannot be empty")
        if not self.path:
            raise ValueError("iaac finding path cannot be empty")
