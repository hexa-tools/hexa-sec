"""DnsRecord — a DNS entry found during enumeration (context: dns_risk)."""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.dns_risk.record_type import RecordType


@dataclass(frozen=True)
class DnsRecord:
    """A single DNS record."""

    name: str
    record_type: RecordType
    value: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("dns record name cannot be empty")
        if not isinstance(self.record_type, RecordType):
            raise ValueError("dns record record_type must be a RecordType")
        if not self.value:
            raise ValueError("dns record value cannot be empty")
