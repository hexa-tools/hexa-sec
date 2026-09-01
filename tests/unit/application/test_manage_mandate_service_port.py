"""Tests for ManageMandateServicePort (driving port — US-4)."""

from __future__ import annotations

import inspect

from hexa_sec.application.ports.driving.manage_mandate.manage_mandate_service_port import (
    ManageMandateServicePort,
)


def test_manage_mandate_service_port_is_abstract() -> None:
    assert inspect.isabstract(ManageMandateServicePort) is True
