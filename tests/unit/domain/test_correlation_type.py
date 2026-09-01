"""Tests for CorrelationType (context: correlation)."""

from __future__ import annotations

from hexa_sec.domain.correlation.correlation_type import CorrelationType


def test_correlation_type_members() -> None:
    assert CorrelationType.ATTACK_CHAIN.value == "attack-chain"
    assert CorrelationType.EXPOSURE.value == "exposure"
    assert CorrelationType.NOISE_REDUCTION.value == "noise-reduction"
    assert CorrelationType.TEMPORAL.value == "temporal"
    assert CorrelationType.COMPLIANCE.value == "compliance"
    assert CorrelationType.BUSINESS_IMPACT.value == "business-impact"


def test_correlation_type_is_unique() -> None:
    values = [member.value for member in CorrelationType]
    assert len(values) == len(set(values))
