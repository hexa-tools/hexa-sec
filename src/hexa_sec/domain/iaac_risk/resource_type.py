"""ResourceType — the IaC resource families (context: iaac_risk, SEC-17).

The type of a risky IaC resource, and its imposed severity floor: a public
bucket / too-open security group is at least HIGH — never LOW. A generic
terraform/helm file carries no imposed floor (the scanner's severity stands).
Normalization never invents a type.
"""

from __future__ import annotations

from enum import Enum

from hexa_sec.domain.finding.severity import Severity


class ResourceType(Enum):
    """The cloud/IaC resource families audited by checkov."""

    AWS_S3_BUCKET = "aws_s3_bucket"
    AWS_SECURITY_GROUP = "aws_security_group"
    AWS_IAM_ROLE = "aws_iam_role"
    AZURE_STORAGE_ACCOUNT = "azure_storage_account"
    GCP_STORAGE_BUCKET = "gcp_storage_bucket"
    TERRAFORM = "terraform"
    HELM = "helm"

    def min_severity(self) -> Severity:
        """The minimum severity imposed by this resource type.

        Only a public bucket is mandated (never LOW); other cloud resources keep
        the scanner's severity — an over-broad floor would drop legitimate
        MEDIUM/LOW findings for security groups, IAM roles or storage accounts.
        """
        if self is ResourceType.AWS_S3_BUCKET:
            return Severity.HIGH
        return Severity.LOW

    @classmethod
    def normalize(cls, raw: str) -> ResourceType:
        """Map a raw label to a ``ResourceType``; unknown values are rejected."""
        cleaned = raw.strip().lower().replace(" ", "_").replace("-", "_")
        try:
            return cls(cleaned)
        except ValueError as error:
            raise ValueError(f"unknown resource type: {raw}") from error
