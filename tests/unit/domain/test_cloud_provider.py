"""Tests for CloudProvider (context: cloud_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.cloud_risk.cloud_provider import CloudProvider


def test_cloud_provider_values() -> None:
    assert CloudProvider.AWS.value == "aws"
    assert CloudProvider.AZURE.value == "azure"
    assert CloudProvider.GCP.value == "gcp"


def test_cloud_provider_is_unique() -> None:
    values = [member.value for member in CloudProvider]
    assert len(values) == len(set(values))


def test_cloud_provider_normalize_accepts_known() -> None:
    assert CloudProvider.normalize("aws") is CloudProvider.AWS
    assert CloudProvider.normalize("AZURE") is CloudProvider.AZURE
    assert CloudProvider.normalize("gcp") is CloudProvider.GCP


def test_cloud_provider_normalize_rejects_unknown() -> None:
    with pytest.raises(ValueError):
        CloudProvider.normalize("oci")


def test_cloud_provider_normalize_rejects_blank() -> None:
    with pytest.raises(ValueError):
        CloudProvider.normalize("   ")
