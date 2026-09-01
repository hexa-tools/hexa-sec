"""Base exception hierarchy for hexa-sec (US-0).

Pure domain — imports nothing external. Every exception is a subclass of
:class:`HexaSecError` so any layer can catch a single base type and read
structured ``context``. Messages describe *what* failed in plain terms; the
presentation layer (CLI/MCP) is responsible for user-facing rendering.

Subclasses are grouped by domain. Secondary scanner adapters translate their
native exceptions (HTTPError, TimeoutError, ApiException) into the
``Scanner*Error`` family — never letting an infra exception escape.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


class HexaSecError(Exception):
    """Base exception for all hexa-sec errors."""

    def __init__(
        self,
        message: str,
        context: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.context: dict[str, str] = dict(context or {})


@dataclass(frozen=True)
class ErrorOrigin:
    """The bounded context an error belongs to (readable, testable label)."""

    context: str


# ── Consent / mandate (law Godfrain) ──────────────────────────────────
class MandateNotFoundError(HexaSecError):
    """No mandate exists for the requested scan. Blocks the scan."""


class MandateScopeError(HexaSecError):
    """The target falls outside the mandate's exact scope. Blocks the scan."""


class MandateExpiredError(HexaSecError):
    """The mandate is no longer within its validity period. Blocks the scan."""


class MandateLevelError(HexaSecError):
    """The mandate level (standard) is insufficient for an offensive tool."""


# ── Scanners (secondary adapters) ─────────────────────────────────────
class ScannerUnavailableError(HexaSecError):
    """A scanner backend could not be reached."""


class ScannerAuthError(HexaSecError):
    """Missing or invalid credentials.

    Never carries the secret itself — generic message only.
    """


class ScannerTimeoutError(HexaSecError):
    """A scanner call exceeded its timeout."""


class ScannerParseError(HexaSecError):
    """The scanner output could not be parsed into domain objects."""


# ── Correlation (the product's core) ──────────────────────────────────
class CorrelationError(HexaSecError):
    """A correlation could not be built (missing evidence, invalid input)."""


# ── Persistence / reporting ───────────────────────────────────────────
class ReportStoreError(HexaSecError):
    """Persistence backend failure for reports or the audit trail."""


class TenantIsolationError(HexaSecError):
    """A tenant scoped operation crossed tenant boundaries."""
