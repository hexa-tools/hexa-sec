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
