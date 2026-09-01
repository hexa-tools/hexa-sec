"""Tests for CorrelateServicePort (driving port — US-2)."""

from __future__ import annotations

import inspect

from hexa_sec.application.ports.driving.correlate.correlate_service_port import CorrelateServicePort


def test_correlate_service_port_is_abstract() -> None:
    assert inspect.isabstract(CorrelateServicePort) is True
