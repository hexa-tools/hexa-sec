"""Container — the composition root (wired application graph)."""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.application.use_case.correlate.correlate_use_case import CorrelateUseCase
from hexa_sec.application.use_case.generate_report.generate_report_use_case import (
    GenerateReportUseCase,
)
from hexa_sec.application.use_case.manage_mandate.manage_mandate_use_case import (
    ManageMandateUseCase,
)
from hexa_sec.application.use_case.scan_asset.scan_asset_use_case import ScanAssetUseCase
from hexa_sec.application.use_case.score_report.score_report_use_case import ScoreReportUseCase
from hexa_sec.infrastructure.config.settings import DefaultSettings


@dataclass(frozen=True)
class Container:
    """The wired application graph consumed by primary adapters."""

    scan_asset: ScanAssetUseCase
    correlate: CorrelateUseCase
    score_report: ScoreReportUseCase
    manage_mandate: ManageMandateUseCase
    generate_report: GenerateReportUseCase
    settings: DefaultSettings


def build_container() -> Container:
    """Wire the services into the use cases (Phase 2 swaps the real services)."""
    from hexa_sec.application.service.correlate_service import CorrelateService
    from hexa_sec.application.service.generate_report_service import GenerateReportService
    from hexa_sec.application.service.manage_mandate_service import ManageMandateService
    from hexa_sec.application.service.scan_asset_service import ScanAssetService
    from hexa_sec.application.service.score_report_service import ScoreReportService

    return Container(
        scan_asset=ScanAssetUseCase(ScanAssetService()),
        correlate=CorrelateUseCase(CorrelateService()),
        score_report=ScoreReportUseCase(ScoreReportService()),
        manage_mandate=ManageMandateUseCase(ManageMandateService()),
        generate_report=GenerateReportUseCase(GenerateReportService()),
        settings=DefaultSettings(),
    )
