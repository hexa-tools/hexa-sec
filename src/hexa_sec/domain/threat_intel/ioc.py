"""Ioc + IocType — an indicator of compromise (context: threat_intel, SEC-20).

An IOC (ip, domain, hash, url) always carries a type — never guessed. The value
is normalized (stripped).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class IocType(Enum):
    """The kind of an indicator of compromise."""

    IP = "ip"
    DOMAIN = "domain"
    HASH = "hash"
    URL = "url"

    @classmethod
    def normalize(cls, raw: str) -> IocType:
        """Map a raw label to an ``IocType``; unknown values are rejected."""
        cleaned = raw.strip().lower().replace(" ", "_").replace("-", "_")
        try:
            return cls(cleaned)
        except ValueError as error:
            raise ValueError(f"unknown ioc type: {raw}") from error


@dataclass(frozen=True)
class Ioc:
    """A single indicator of compromise."""

    value: str
    ioc_type: IocType

    def __post_init__(self) -> None:
        if not self.value or not self.value.strip():
            raise ValueError("ioc value cannot be empty")
        if not isinstance(self.ioc_type, IocType):
            raise ValueError("ioc type must be an IocType")
        object.__setattr__(self, "value", self.value.strip())
