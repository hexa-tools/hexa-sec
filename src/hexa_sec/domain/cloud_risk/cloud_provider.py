"""CloudProvider — the cloud platforms audited (context: cloud_risk)."""

from __future__ import annotations

from enum import Enum


class CloudProvider(Enum):
    """A supported cloud vendor."""

    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
