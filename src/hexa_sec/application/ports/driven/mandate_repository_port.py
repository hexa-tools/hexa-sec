"""MandateRepositoryPort — resolve a mandate by id (US-1, driven port).

The mandate is the non-negotiable Godfrain gate: the service fetches it here
before launching any scanner. ``load`` is fail-closed — an unknown id returns
``None``, never a fabricated mandate.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from hexa_sec.domain.consent.mandate import Mandate


class MandateRepositoryPort(ABC):
    """Resolve a mandate by its identifier."""

    @abstractmethod
    def load(self, mandate_id: str) -> Mandate | None:
        """Return the mandate ``mandate_id`` or ``None`` if unknown.

        Raises:
            TenantIsolationError: when the access is not scoped to a tenant.
        """
        raise NotImplementedError  # pragma: no cover
