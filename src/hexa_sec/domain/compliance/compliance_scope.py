"""ComplianceScope — the accountability frameworks (context: compliance)."""

from __future__ import annotations

from enum import Enum


class ComplianceScope(Enum):
    """Compliance frameworks hexa-sec scores against."""

    ISO_27001 = "iso_27001"
    RGPD = "rgpd"
    NIS2 = "nis2"
    PCI_DSS = "pci_dss"
