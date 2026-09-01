"""VendorConfig — the declared scanner keys (context: pack_config).

Declares the environment-variable key NAMES a vendor needs — never the values.
A key that is value-like (contains ``=``) or a secret pattern is rejected; the
actual values live in the SecretStore, never here.
"""

from __future__ import annotations

from dataclasses import dataclass

_SECRET_MARKERS = ("sk-", "AKIA", "-----BEGIN")


@dataclass(frozen=True)
class VendorConfig:
    """The declared environment key names for one vendor."""

    provider: str
    keys: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.provider.strip():
            raise ValueError("vendor provider cannot be empty")
        normalized: list[str] = []
        for key in self.keys:
            cleaned = key.strip()
            if not cleaned:
                raise ValueError("vendor key cannot be empty")
            if "=" in cleaned or any(marker in cleaned for marker in _SECRET_MARKERS):
                raise ValueError("vendor config key must be a name, never a value")
            normalized.append(cleaned)
        object.__setattr__(self, "provider", self.provider.strip())
        object.__setattr__(self, "keys", tuple(normalized))
