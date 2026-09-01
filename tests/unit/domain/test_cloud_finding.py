"""Tests for CloudFinding (context: cloud_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.cloud_risk.cloud_finding import CloudFinding
from hexa_sec.domain.cloud_risk.cloud_provider import CloudProvider
from hexa_sec.domain.cloud_risk.cloud_resource import CloudResource
from hexa_sec.domain.finding.severity import Severity


def _public_resource() -> CloudResource:
    return CloudResource(
        provider=CloudProvider.AWS,
        resource_id="arn:aws:s3:::data",
        resource_type="aws_s3_bucket",
        public=True,
    )


def _private_resource() -> CloudResource:
    return CloudResource(
        provider=CloudProvider.AWS,
        resource_id="arn:aws:s3:::data",
        resource_type="aws_s3_bucket",
    )


def test_cloud_finding_creation() -> None:
    finding = CloudFinding(resource=_public_resource(), issue="public bucket", severity=Severity.HIGH)
    assert finding.issue == "public bucket"
    assert finding.severity is Severity.HIGH


def test_cloud_finding_default_severity() -> None:
    finding = CloudFinding(resource=_public_resource(), issue="public bucket")
    assert finding.severity is Severity.MEDIUM


def test_cloud_finding_exposed() -> None:
    assert CloudFinding(resource=_public_resource(), issue="x").exposed() is True
    assert CloudFinding(resource=_private_resource(), issue="x").exposed() is False


def test_cloud_finding_rejects_empty_issue() -> None:
    with pytest.raises(ValueError):
        CloudFinding(resource=_public_resource(), issue="")
