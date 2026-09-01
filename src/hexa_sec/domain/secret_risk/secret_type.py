"""SecretType — the kinds of detected secrets (context: secret_risk)."""

from __future__ import annotations

from enum import Enum


class SecretType(Enum):
    """Classification of a committed secret."""

    API_KEY = "api_key"
    PASSWORD = "password"
    TOKEN = "token"
