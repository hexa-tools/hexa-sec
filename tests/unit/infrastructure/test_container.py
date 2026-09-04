"""Tests for the composition root (Container)."""

from __future__ import annotations

from hexa_sec.application.use_case.correlate.correlate_use_case import CorrelateUseCase
from hexa_sec.application.use_case.generate_report.generate_report_use_case import (
    GenerateReportUseCase,
)
from hexa_sec.application.use_case.manage_mandate.manage_mandate_use_case import (
    ManageMandateUseCase,
)
from hexa_sec.application.use_case.scan_asset.scan_asset_use_case import ScanAssetUseCase
from hexa_sec.application.use_case.score_report.score_report_use_case import ScoreReportUseCase
from hexa_sec.infrastructure.bootstrap.container import Container, build_container


def test_build_container_wires_every_use_case_with_a_service() -> None:
    container = build_container()
    assert isinstance(container.scan_asset, ScanAssetUseCase)
    assert isinstance(container.correlate, CorrelateUseCase)
    assert isinstance(container.score_report, ScoreReportUseCase)
    assert isinstance(container.manage_mandate, ManageMandateUseCase)
    assert isinstance(container.generate_report, GenerateReportUseCase)
    assert container.scan_asset._service is not None
    assert container.correlate._service is not None
    assert container.score_report._service is not None
    assert container.manage_mandate._service is not None
    assert container.generate_report._service is not None


def test_container_exposes_settings() -> None:
    container = build_container()
    assert container.settings.pack_name == "hexa-sec"


def test_container_partial_is_frozen() -> None:
    container = build_container()
    field_names = {field.name for field in Container.__dataclass_fields__.values()}
    assert "scan_asset" in field_names
