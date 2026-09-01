"""DefaultSettings — the pack-wide defaults (infrastructure)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DefaultSettings:
    """Static, non-secret configuration.

    Secrets never live here — they are fetched from the SecretStorePort.
    """

    pack_name: str = "hexa-sec"
    pack_entrypoint: str = "mcp://hexa-sec"
    default_vendor: str = "nessus"
