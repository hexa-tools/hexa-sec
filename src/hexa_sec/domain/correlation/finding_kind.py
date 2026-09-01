"""FindingKind — the normalized category of a finding (context: correlation)."""

from __future__ import annotations

from enum import Enum


class FindingKind(Enum):
    """The kind of scanner finding, normalized for deterministic correlation.

    Adapters (Phase 3) translate each scanner output into a :class:`FindingKind`
    so the checker can cross them without knowing the scanner.
    """

    VULNERABILITY = "vulnerability"
    SQL_INJECTION = "sql_injection"
    SECRET = "secret"
    EXPOSED_PORT = "exposed_port"
    TLS = "tls"
    MISCONFIG = "misconfig"
    API = "api"
    LOGIN = "login"
    COMPLIANCE = "compliance"
    NOISE = "noise"
