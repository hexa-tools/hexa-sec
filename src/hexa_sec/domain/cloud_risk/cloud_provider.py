"""CloudProvider — the cloud platforms audited (context: cloud_risk)."""

from __future__ import annotations

from enum import Enum


class CloudProvider(Enum):
    """A supported cloud vendor."""

    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"

    @classmethod
    def normalize(cls, raw: str) -> CloudProvider:
        """Map a raw label to a ``CloudProvider``; unknown values are rejected."""
        cleaned = raw.strip().lower().replace(" ", "_").replace("-", "_")
        try:
            return cls(cleaned)
        except ValueError as error:
            raise ValueError(f"unknown cloud provider: {raw}") from error
