"""CloudResource — a cloud resource and its exposure (context: cloud_risk)."""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.cloud_risk.cloud_provider import CloudProvider


@dataclass(frozen=True)
class CloudResource:
    """A single cloud resource under audit."""

    provider: CloudProvider
    resource_id: str
    resource_type: str
    public: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.provider, CloudProvider):
            raise ValueError("cloud resource provider must be a CloudProvider")
        if not self.resource_id.strip():
            raise ValueError("cloud resource id cannot be empty")
        if not self.resource_type.strip():
            raise ValueError("cloud resource type cannot be empty")
        object.__setattr__(self, "resource_id", self.resource_id.strip())
        object.__setattr__(self, "resource_type", self.resource_type.strip())

    def is_public(self) -> bool:
        return self.public
