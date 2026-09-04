"""RecordType — the DNS record types relevant to enumeration (context: dns_risk)."""

from __future__ import annotations

from enum import Enum


class RecordType(Enum):
    """DNS record types observed during enumeration."""

    A = "a"
    AAAA = "aaaa"
    CNAME = "cname"
    MX = "mx"
    TXT = "txt"
    NS = "ns"
    SOA = "soa"

    @classmethod
    def normalize(cls, raw: str) -> RecordType:
        """Map a raw label to a ``RecordType``; unknown values are rejected."""
        cleaned = raw.strip().lower()
        try:
            return cls(cleaned)
        except ValueError as error:
            raise ValueError(f"unknown record type: {raw}") from error
