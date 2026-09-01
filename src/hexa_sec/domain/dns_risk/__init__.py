"""Bound context — DNS risk (forgotten subdomains, zone transfer, records)."""

from __future__ import annotations

from hexa_sec.domain.dns_risk.dns_finding import DnsFinding
from hexa_sec.domain.dns_risk.dns_record import DnsRecord
from hexa_sec.domain.dns_risk.record_type import RecordType
from hexa_sec.domain.dns_risk.subdomain import Subdomain

__all__ = ["DnsFinding", "DnsRecord", "RecordType", "Subdomain"]
