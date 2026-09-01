"""AssetCriticality — the business criticality of an asset (context: asset)."""

from __future__ import annotations

from enum import Enum


class AssetCriticality(Enum):
    """Business weight of an asset, used by the business-impact correlation.

    Higher ``weight`` means a breach on this asset has worse business
    consequences.
    """

    ERP = "erp"
    CRM = "crm"
    PARTNER = "partner"
    INTERNAL = "internal"
    PUBLIC = "public"

    @property
    def weight(self) -> int:
        return {
            AssetCriticality.ERP: 5,
            AssetCriticality.CRM: 4,
            AssetCriticality.PARTNER: 3,
            AssetCriticality.INTERNAL: 2,
            AssetCriticality.PUBLIC: 1,
        }[self]
