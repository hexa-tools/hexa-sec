"""Tests for IaacFinding (context: iaac_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.iaac_risk.iaac_finding import IaacFinding


def test_iaac_finding_creation() -> None:
    finding = IaacFinding(resource_type="aws_s3_bucket", path="infra/main.tf")
    assert finding.resource_type == "aws_s3_bucket"


def test_iaac_finding_rejects_empty_resource_type() -> None:
    with pytest.raises(ValueError):
        IaacFinding(resource_type="", path="infra/main.tf")


def test_iaac_finding_rejects_empty_path() -> None:
    with pytest.raises(ValueError):
        IaacFinding(resource_type="aws_s3_bucket", path="")
