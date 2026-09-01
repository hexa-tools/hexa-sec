"""Tests for CloudProvider (context: cloud_risk)."""

from __future__ import annotations

from hexa_sec.domain.cloud_risk.cloud_provider import CloudProvider


def test_cloud_provider_values() -> None:
    assert CloudProvider.AWS.value == "aws"
    assert CloudProvider.AZURE.value == "azure"
    assert CloudProvider.GCP.value == "gcp"


def test_cloud_provider_is_unique() -> None:
    values = [member.value for member in CloudProvider]
    assert len(values) == len(set(values))
