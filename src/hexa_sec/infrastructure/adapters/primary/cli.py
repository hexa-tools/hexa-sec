"""hexa-sec CLI — the pack control surface (primary adapter)."""

from __future__ import annotations

import click

from hexa_sec.application.ports.driving.correlate.correlate_service_port import CorrelateResult
from hexa_sec.application.ports.driving.generate_report.generate_report_service_port import (
    GenerateReportResult,
)
from hexa_sec.application.ports.driving.manage_mandate.manage_mandate_service_port import (
    ManageMandateResult,
)
from hexa_sec.application.ports.driving.scan_asset.scan_asset_service_port import ScanAssetResult
from hexa_sec.application.service.correlate_service import CorrelateService
from hexa_sec.application.service.generate_report_service import GenerateReportService
from hexa_sec.application.service.manage_mandate_service import ManageMandateService
from hexa_sec.application.service.scan_asset_service import ScanAssetService
from hexa_sec.application.use_case.correlate.correlate_use_case import CorrelateUseCase
from hexa_sec.application.use_case.generate_report.generate_report_use_case import (
    GenerateReportUseCase,
)
from hexa_sec.application.use_case.manage_mandate.manage_mandate_use_case import (
    ManageMandateUseCase,
)
from hexa_sec.application.use_case.scan_asset.scan_asset_use_case import ScanAssetUseCase
from hexa_sec.infrastructure.adapters.primary.mcp_server import (
    correlate_handler,
    generate_report_handler,
    manage_mandate_handler,
    scan_asset_handler,
)


def _scan_use_case() -> ScanAssetUseCase:
    return ScanAssetUseCase(ScanAssetService())


def _correlate_use_case() -> CorrelateUseCase:
    return CorrelateUseCase(CorrelateService())


def _mandate_use_case() -> ManageMandateUseCase:
    return ManageMandateUseCase(ManageMandateService())


def _report_use_case() -> GenerateReportUseCase:
    return GenerateReportUseCase(GenerateReportService())


def build_cli() -> click.Group:
    """Return the root click group with the four scanning commands."""

    @click.group()
    def cli() -> None:
        """hexa-sec — orchestrate scanners and correlate their findings."""

    @cli.command(name="scan")
    @click.option("--asset", required=True)
    @click.option("--mandate-id", required=True)
    @click.option("--vendor", default="nessus")
    @click.option("--tenant-id", required=True)
    def scan_cmd(asset: str, mandate_id: str, vendor: str, tenant_id: str) -> ScanAssetResult:
        """Lancer un scan — le mandat est vérifié avant (loi Godfrain)."""
        return scan_asset_handler(_scan_use_case(), asset, mandate_id, vendor, tenant_id)

    @cli.command(name="correlate")
    @click.option("--scan-id", required=True)
    def correlate_cmd(scan_id: str) -> CorrelateResult:
        """Corréler les findings d'un scan."""
        return correlate_handler(_correlate_use_case(), scan_id)

    @cli.command(name="report")
    @click.option("--scan-id", required=True)
    def report_cmd(scan_id: str) -> GenerateReportResult:
        """Générer le rapport client."""
        return generate_report_handler(_report_use_case(), scan_id)

    @cli.command(name="mandate")
    @click.option("--client", required=True)
    @click.option("--target", multiple=True, required=True)
    @click.option("--start", required=True)
    @click.option("--end", required=True)
    @click.option("--level", default="standard")
    @click.option("--signature", required=True)
    @click.option("--actor", default="operator")
    @click.option("--tenant-id", required=True)
    def mandate_cmd(
        client: str,
        target: tuple[str, ...],
        start: str,
        end: str,
        level: str,
        signature: str,
        actor: str,
        tenant_id: str,
    ) -> ManageMandateResult:
        """Enregistrer le consentement légal mandat."""
        return manage_mandate_handler(
            _mandate_use_case(),
            client,
            list(target),
            start,
            end,
            level,
            signature,
            actor,
            tenant_id,
        )

    return cli


cli: click.Group = build_cli()
