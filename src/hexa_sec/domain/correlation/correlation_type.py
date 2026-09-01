"""CorrelationType — the six deterministic correlations (context: correlation)."""

from __future__ import annotations

from enum import Enum


class CorrelationType(Enum):
    """The correlation families hexa-sec produces. All are deterministic."""

    ATTACK_CHAIN = "attack-chain"
    EXPOSURE = "exposure"
    NOISE_REDUCTION = "noise-reduction"
    TEMPORAL = "temporal"
    COMPLIANCE = "compliance"
    BUSINESS_IMPACT = "business-impact"
