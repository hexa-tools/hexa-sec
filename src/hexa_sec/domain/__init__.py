"""The pure domain of hexa-sec.

``domain/`` imports nothing external: no scanner SDK, no HTTP, no CLI, no
infrastructure. It only depends on the Python standard library. Each folder is
one bounded context.

Consent is here from the bootstrap: a scan is never legal without a mandate.
"""

from __future__ import annotations

from hexa_sec.domain.errors import HexaSecError

__all__ = ["HexaSecError"]
