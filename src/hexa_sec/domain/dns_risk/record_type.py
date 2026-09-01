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
