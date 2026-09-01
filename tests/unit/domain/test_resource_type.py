"""Tests for the ResourceType enum (context: iaac_risk, SEC-17)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.iaac_risk.resource_type import ResourceType


def test_resource_type_members() -> None:
    assert ResourceType.AWS_S3_BUCKET.value == "aws_s3_bucket"
    assert ResourceType.AWS_SECURITY_GROUP.value == "aws_security_group"
    assert ResourceType.AWS_IAM_ROLE.value == "aws_iam_role"
    assert ResourceType.AZURE_STORAGE_ACCOUNT.value == "azure_storage_account"
    assert ResourceType.GCP_STORAGE_BUCKET.value == "gcp_storage_bucket"
    assert ResourceType.TERRAFORM.value == "terraform"
    assert ResourceType.HELM.value == "helm"


def test_resource_type_unique_values() -> None:
    values = [member.value for member in ResourceType]
    assert len(values) == len(set(values))


def test_resource_type_normalize_accepts_known_values() -> None:
    assert ResourceType.normalize("aws s3 bucket") is ResourceType.AWS_S3_BUCKET
    assert ResourceType.normalize("AWS_SECURITY_GROUP") is ResourceType.AWS_SECURITY_GROUP
    assert ResourceType.normalize("azure_storage_account") is ResourceType.AZURE_STORAGE_ACCOUNT
    assert ResourceType.normalize("terraform") is ResourceType.TERRAFORM
    assert ResourceType.normalize("helm") is ResourceType.HELM


def test_resource_type_normalize_rejects_unknown() -> None:
    with pytest.raises(ValueError):
        ResourceType.normalize("k8s_cronjob")


def test_resource_type_normalize_rejects_blank() -> None:
    with pytest.raises(ValueError):
        ResourceType.normalize("   ")


def test_resource_type_min_severity_public_bucket_at_least_high() -> None:
    assert ResourceType.AWS_S3_BUCKET.min_severity().rank >= Severity.HIGH.rank


def test_resource_type_min_severity_other_cloud_no_floor() -> None:
    assert ResourceType.AWS_SECURITY_GROUP.min_severity() is Severity.LOW
    assert ResourceType.AWS_IAM_ROLE.min_severity() is Severity.LOW
    assert ResourceType.AZURE_STORAGE_ACCOUNT.min_severity() is Severity.LOW
    assert ResourceType.GCP_STORAGE_BUCKET.min_severity() is Severity.LOW


def test_resource_type_min_severity_generic_no_floor() -> None:
    assert ResourceType.TERRAFORM.min_severity() is Severity.LOW
    assert ResourceType.HELM.min_severity() is Severity.LOW
