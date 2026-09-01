"""OwaspCategory — the OWASP Top 10 web risk categories (context: web_risk)."""

from __future__ import annotations

from enum import Enum


class OwaspCategory(Enum):
    """The OWASP Top 10 (2021) web application risk categories."""

    BROKEN_ACCESS_CONTROL = "a01"
    CRYPTOGRAPHIC_FAILURES = "a02"
    INJECTION = "a03"
    INSECURE_DESIGN = "a04"
    SECURITY_MISCONFIGURATION = "a05"
    VULNERABLE_AND_OUTDATED_COMPONENTS = "a06"
    IDENTIFICATION_AND_AUTHENTICATION_FAILURES = "a07"
    SOFTWARE_AND_DATA_INTEGRITY_FAILURES = "a08"
    SECURITY_LOGGING_AND_MONITORING_FAILURES = "a09"
    SERVER_SIDE_REQUEST_FORGERY = "a10"

    @property
    def order(self) -> int:
        return int(self.value[1:])

    @classmethod
    def from_code(cls, code: str) -> OwaspCategory:
        return cls(code.strip().lower())

    @classmethod
    def normalize(cls, raw: str) -> OwaspCategory:
        """Map ``"A03"`` or ``"a03"`` to an enum; unknown -> ValueError.

        Never invents a category: an unrecognized value is rejected at
        normalization time.
        """
        code = raw.strip().lower()
        if not code.startswith("a") or not code[1:].isdigit():
            raise ValueError(f"invalid OWASP category: {raw}")
        try:
            return cls(code)
        except ValueError as error:
            raise ValueError(f"unknown OWASP category: {raw}") from error
