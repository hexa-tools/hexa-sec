"""Tests for CloudResource (context: cloud_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.cloud_risk.cloud_provider import CloudProvider
from hexa_sec.domain.cloud_risk.cloud_resource import CloudResource


def test_cloud_resource_creation() -> None:
    resource = CloudResource(
        provider=CloudProvider.AWS,
        resource_id="arn:aws:s3:::data",
        resource_type="aws_s3_bucket",
        public=True,
    )
    assert resource.provider is CloudProvider.AWS
    assert resource.resource_type == "aws_s3_bucket"
    assert resource.is_public() is True


def test_cloud_resource_default_private() -> None:
    resource = CloudResource(
        provider=CloudProvider.GCP,
        resource_id="bucket",
        resource_type="storage",
    )
    assert resource.is_public() is False


def test_cloud_resource_rejects_empty_id() -> None:
    with pytest.raises(ValueError):
        CloudResource(provider=CloudProvider.AWS, resource_id="", resource_type="aws_s3_bucket")


def test_cloud_resource_rejects_empty_type() -> None:
    with pytest.raises(ValueError):
        CloudResource(provider=CloudProvider.AWS, resource_id="x", resource_type="")
