"""SecretFinding — a committed secret (context: secret_risk, SEC-12).

An adapter (gitleaks/trufflehog/detect-secrets) translates a scanner hit into
a SecretFinding: the asset, its secret type, the evidence (occurrence/location)
and an optional ``revoked`` marker. Without evidence there is no finding, and the
severity always follows the secret type — never a default.

Evidence is mandatory: a secret without proof is a speculation, rejected at
construction.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.secret_risk.secret_severity import SecretSeverity
from hexa_sec.domain.secret_risk.secret_type import SecretType


@dataclass(frozen=True)
class SecretFinding:
    """A single secret detected in a repository."""

    asset: str
    secret_type: SecretType
    evidence: str
    revoked: bool = False

    @property
    def severity(self) -> SecretSeverity:
        """The severity, derived from the secret type (never defaulted)."""
        return SecretSeverity.for_type(self.secret_type)

    def __post_init__(self) -> None:
        if not self.asset or not self.asset.strip():
            raise ValueError("secret finding asset cannot be empty")
        if not isinstance(self.secret_type, SecretType):
            raise ValueError("secret finding secret_type must be a SecretType")
        if not self.evidence or not self.evidence.strip():
            raise ValueError("secret finding requires evidence (proof)")
