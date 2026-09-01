"""SecretFinding — a committed secret (context: secret_risk)."""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.secret_risk.secret_type import SecretType


@dataclass(frozen=True)
class SecretFinding:
    """A token, key or credential found in a repository."""

    path: str
    kind: SecretType

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("secret finding path cannot be empty")
