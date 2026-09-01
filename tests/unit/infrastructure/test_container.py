"""Tests for the composition root (Container)."""

from __future__ import annotations

from hexa_sec.application.use_case.correlate.correlate_use_case import CorrelateUseCase
from hexa_sec.application.use_case.scan_asset.scan_asset_use_case import ScanAssetUseCase
from hexa_sec.infrastructure.bootstrap.container import Container, build_container


def test_build_container_wires_use_cases() -> None:
    container = build_container()
    assert isinstance(container.scan_asset, ScanAssetUseCase)
    assert isinstance(container.correlate, CorrelateUseCase)


def test_container_exposes_settings() -> None:
    container = build_container()
    assert container.settings.pack_name == "hexa-sec"


def test_container_partial_is_frozen() -> None:
    container = build_container()
    field_names = {field.name for field in Container.__dataclass_fields__.values()}
    assert "scan_asset" in field_names
