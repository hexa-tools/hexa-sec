"""SecretSeverity — the sensitivity-derived severity (context: secret_risk, SEC-12).

The severity follows the secret type, never a default: a banal type (anonymized
value) is LOW, a live credential (private key / AWS key / password) is CRITICAL.
The ``sensitive`` flag separates a real credential from an anodyne extract.
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.secret_risk.secret_type import SecretType

_SENSITIVITY: dict[SecretType, tuple[Severity, bool]] = {
    SecretType.PRIVATEKEY: (Severity.CRITICAL, True),
    SecretType.AWSKEY: (Severity.CRITICAL, True),
    SecretType.PASSWORD: (Severity.CRITICAL, True),
    SecretType.TOKEN: (Severity.HIGH, True),
    SecretType.APIKEY: (Severity.HIGH, True),
    SecretType.CIPHERTEXT: (Severity.LOW, False),
}


@dataclass(frozen=True)
class SecretSeverity:
    """The severity of a secret, derived from its type."""

    level: Severity
    sensitive: bool

    @property
    def is_critical(self) -> bool:
        """Whether the secret is a live, must-revoke credential."""
        return self.level is Severity.CRITICAL

    @classmethod
    def for_type(cls, secret_type: SecretType) -> SecretSeverity:
        """Compute the severity from a known secret type.

        Deterministic by construction: a banal type is never CRITICAL by default
        and a sensitive live credential is CRITICAL.
        """
        level, sensitive = _SENSITIVITY[secret_type]
        return cls(level=level, sensitive=sensitive)
