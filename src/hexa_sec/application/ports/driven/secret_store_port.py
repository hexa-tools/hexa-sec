"""SecretStorePort — the encrypted secret boundary (driven port)."""

from __future__ import annotations

from abc import ABC, abstractmethod


class SecretStorePort(ABC):
    """Retrieve per-tenant scanner keys, encrypted at rest.

    A secret is never logged, never put in tests, never returned in clear text
    to a primary adapter. ``ScannerAuthError`` never reveals it.
    """

    @abstractmethod
    def get(self, vendor: str, tenant: str) -> str | None:
        """Return the key for ``vendor`` in ``tenant``, or ``None``."""
        raise NotImplementedError  # pragma: no cover
