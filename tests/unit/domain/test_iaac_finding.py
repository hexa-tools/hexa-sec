"""Tests for IaacFinding (context: iaac_risk, SEC-17)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.iaac_risk.ia_c_file_name import IaCFileName
from hexa_sec.domain.iaac_risk.iaac_finding import IaacFinding
from hexa_sec.domain.iaac_risk.resource_type import ResourceType


def _finding(
    resource_type: ResourceType = ResourceType.AWS_S3_BUCKET,
    path: str = "infra/main.tf",
    severity: Severity = Severity.HIGH,
    evidence: str = "bucket ACL public",
) -> IaacFinding:
    return IaacFinding(
        resource_type=resource_type,
        path=IaCFileName(path),
        severity=severity,
        evidence=evidence,
    )


def test_iaac_finding_creation() -> None:
    finding = _finding()
    assert finding.resource_type is ResourceType.AWS_S3_BUCKET
    assert finding.path.path == "infra/main.tf"
    assert finding.severity is Severity.HIGH
    assert finding.evidence == "bucket ACL public"


def test_iaac_finding_rejects_non_resource_type() -> None:
    with pytest.raises(ValueError):
        IaacFinding(
            resource_type="aws_s3_bucket",
            path=IaCFileName("infra/main.tf"),
            severity=Severity.HIGH,
            evidence="bucket ACL public",
        )


def test_iaac_finding_rejects_non_file_name() -> None:
    with pytest.raises(ValueError):
        IaacFinding(
            resource_type=ResourceType.AWS_S3_BUCKET,
            path="infra/main.tf",
            severity=Severity.HIGH,
            evidence="bucket ACL public",
        )


def test_iaac_finding_rejects_non_severity() -> None:
    with pytest.raises(ValueError):
        IaacFinding(
            resource_type=ResourceType.AWS_S3_BUCKET,
            path=IaCFileName("infra/main.tf"),
            severity="high",
            evidence="bucket ACL public",
        )


def test_iaac_finding_rejects_empty_evidence() -> None:
    with pytest.raises(ValueError):
        _finding(evidence="")


def test_iaac_finding_rejects_blank_evidence() -> None:
    with pytest.raises(ValueError):
        _finding(evidence="   ")


def test_iaac_finding_rejects_public_bucket_low() -> None:
    with pytest.raises(ValueError):
        _finding(severity=Severity.LOW)


def test_iaac_finding_accepts_public_bucket_high() -> None:
    assert _finding(severity=Severity.HIGH).severity is Severity.HIGH
    assert _finding(severity=Severity.CRITICAL).severity is Severity.CRITICAL


def test_iaac_finding_accepts_generic_low() -> None:
    assert (
        _finding(resource_type=ResourceType.TERRAFORM, severity=Severity.LOW).severity
        is Severity.LOW
    )


def test_iaac_finding_accepts_security_group_medium() -> None:
    assert (
        _finding(resource_type=ResourceType.AWS_SECURITY_GROUP, severity=Severity.MEDIUM).severity
        is Severity.MEDIUM
    )
