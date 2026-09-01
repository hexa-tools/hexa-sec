"""Bound context 27 — Email risk (SPF/DKIM/DMARC spoofing)."""

from __future__ import annotations

from hexa_sec.domain.email_risk.dmarc_status import DmarcStatus
from hexa_sec.domain.email_risk.email_finding import EmailFinding
from hexa_sec.domain.email_risk.email_record import EmailRecord
from hexa_sec.domain.email_risk.email_risk import EmailRisk

__all__ = ["DmarcStatus", "EmailFinding", "EmailRecord", "EmailRisk"]
