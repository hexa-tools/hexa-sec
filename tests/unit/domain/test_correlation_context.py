"""Tests for CorrelationContext (context: correlation)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.correlation.correlation_context import CorrelationContext


def test_correlation_context_defaults() -> None:
    context = CorrelationContext()
    assert context.exposure_open_ports == 3
    assert context.noise_count == 10
    assert context.previous == ()
    assert context.asset_criticalities == {}


def test_correlation_context_rejects_invalid_thresholds() -> None:
    with pytest.raises(ValueError):
        CorrelationContext(exposure_open_ports=0)
    with pytest.raises(ValueError):
        CorrelationContext(noise_count=-1)
