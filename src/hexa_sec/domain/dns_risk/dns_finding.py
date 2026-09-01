"""DnsFinding — a DNS enumeration exposure (context: dns_risk)."""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.dns_risk.dns_record import DnsRecord
from hexa_sec.domain.dns_risk.subdomain import Subdomain


@dataclass(frozen=True)
class DnsFinding:
    """The exposed DNS surface of a domain."""

    domain: str
    records: tuple[DnsRecord, ...] = ()
    subdomains: tuple[Subdomain, ...] = ()
    zone_transfer: bool = False

    def __post_init__(self) -> None:
        if not self.domain.strip():
            raise ValueError("dns finding domain cannot be empty")

    def has_zone_transfer(self) -> bool:
        return self.zone_transfer

    def exposed(self) -> bool:
        return any(subdomain.resolved for subdomain in self.subdomains)
