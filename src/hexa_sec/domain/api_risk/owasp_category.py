"""OwaspApiCategory — the OWASP API Security Top 10 (context: api_risk)."""

from __future__ import annotations

from enum import Enum


class OwaspApiCategory(Enum):
    """The OWASP API Security Top 10 risk categories."""

    BROKEN_OBJECT_LEVEL_AUTHORIZATION = "api1"
    BROKEN_AUTHENTICATION = "api2"
    BROKEN_OBJECT_PROPERTY_LEVEL_AUTHORIZATION = "api3"
    UNRESTRICTED_RESOURCE_CONSUMPTION = "api4"
    BROKEN_FUNCTION_LEVEL_AUTHORIZATION = "api5"
    UNRESTRICTED_ACCESS_TO_SENSITIVE_BUSINESS_FLOWS = "api6"
    SERVER_SIDE_REQUEST_FORGERY = "api7"
    SECURITY_MISCONFIGURATION = "api8"
    IMPROPER_INVENTORY_MANAGEMENT = "api9"
    UNSAFE_CONSUMPTION_OF_APIS = "api10"

    @classmethod
    def normalize(cls, raw: str) -> OwaspApiCategory:
        """Map ``"API1"``/``"api05"``/``"10"`` to a category; unknown -> ValueError.

        Never invents a category: an unrecognized value is rejected at
        normalization time.
        """
        code = raw.strip().lower()
        if code.startswith("api"):
            code = code[3:]
        code = code.lstrip("0") or "0"
        if code.isdigit() and 1 <= int(code) <= 10:
            return cls(f"api{int(code)}")
        raise ValueError(f"unknown OWASP API category: {raw}")
