"""Tests for the CloudRisk aggregate (context: cloud_risk)."""

from __future__ import annotations

from hexa_sec.domain.cloud_risk.cloud_finding import CloudFinding
from hexa_sec.domain.cloud_risk.cloud_provider import CloudProvider
from hexa_sec.domain.cloud_risk.cloud_resource import CloudResource
from hexa_sec.domain.cloud_risk.cloud_risk import CloudRisk
from hexa_sec.domain.finding.severity import Severity


def _public_finding(resource_id: str) -> CloudFinding:
    resource = CloudResource(
        provider=CloudProvider.AWS,
        resource_id=resource_id,
        resource_type="aws_s3_bucket",
        public=True,
    )
    return CloudFinding(resource=resource, issue="misconfigured", severity=Severity.HIGH)


def _private_finding(resource_id: str) -> CloudFinding:
    resource = CloudResource(
        provider=CloudProvider.AWS,
        resource_id=resource_id,
        resource_type="aws_s3_bucket",
    )
    return CloudFinding(resource=resource, issue="misconfigured", severity=Severity.HIGH)


def test_of_consolidates_findings() -> None:
    findings = (_public_finding("arn:aws:s3:::data"), _private_finding("arn:aws:s3:::logs"))
    risk = CloudRisk.of(findings)
    assert len(risk.findings) == 2
    assert risk.exposed_count == 1


def test_of_deduplicates_same_resource() -> None:
    findings = (_public_finding("arn:aws:s3:::data"), _private_finding("arn:aws:s3:::data"))
    risk = CloudRisk.of(findings)
    assert len(risk.findings) == 1


def test_of_keeps_exposed_resource() -> None:
    findings = (_private_finding("arn:aws:s3:::data"), _public_finding("arn:aws:s3:::data"))
    risk = CloudRisk.of(findings)
    assert len(risk.findings) == 1
    assert risk.findings[0].exposed() is True


# --- Category: concurrence / ordre (ordre total : exposé > sévérité) -------
def test_of_dedup_keeps_higher_severity() -> None:
    high = CloudFinding(
        CloudResource(CloudProvider.AWS, "arn:aws:s3:::data", "aws_s3_bucket", public=True),
        "public bucket",
        Severity.HIGH,
    )
    critical = CloudFinding(
        CloudResource(CloudProvider.AWS, "arn:aws:s3:::data", "aws_s3_bucket", public=True),
        "public bucket",
        Severity.CRITICAL,
    )
    risk = CloudRisk.of((high, critical))
    assert len(risk.findings) == 1
    assert risk.findings[0].severity is Severity.CRITICAL


def test_of_dedup_order_independent_for_severity() -> None:
    high = CloudFinding(
        CloudResource(CloudProvider.AWS, "arn:aws:s3:::data", "aws_s3_bucket", public=True),
        "public bucket",
        Severity.HIGH,
    )
    critical = CloudFinding(
        CloudResource(CloudProvider.AWS, "arn:aws:s3:::data", "aws_s3_bucket", public=True),
        "public bucket",
        Severity.CRITICAL,
    )
    first = CloudRisk.of((high, critical))
    second = CloudRisk.of((critical, high))
    assert first == second
    assert first.findings[0].severity is Severity.CRITICAL


def test_of_exposed_resources() -> None:
    findings = (_public_finding("arn:aws:s3:::data"), _private_finding("arn:aws:s3:::logs"))
    risk = CloudRisk.of(findings)
    assert risk.exposed_resources() == ("arn:aws:s3:::data",)
    assert risk.exposed_count == 1


def test_of_empty_is_empty() -> None:
    risk = CloudRisk.of(())
    assert risk.findings == ()
    assert risk.exposed_count == 0
    assert risk.exposed_resources() == ()


def test_of_is_deterministic() -> None:
    findings = (_public_finding("arn:aws:s3:::data"), _private_finding("arn:aws:s3:::logs"))
    first = CloudRisk.of(findings)
    second = CloudRisk.of(findings)
    assert first == second
    assert first.exposed_count == second.exposed_count


def test_of_order_independent() -> None:
    a = _public_finding("arn:aws:s3:::data")
    b = _private_finding("arn:aws:s3:::logs")
    first = CloudRisk.of((a, b))
    second = CloudRisk.of((b, a))
    assert first == second
    assert [finding.resource.resource_id for finding in first.findings] == [
        finding.resource.resource_id for finding in second.findings
    ]
