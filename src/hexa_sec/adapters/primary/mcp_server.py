"""MCP server — the pack entrypoint (mcp://hexa-sec).

This is the inbound primary adapter. It exposes the 5 tools and delegates to
the use cases. The use cases are thin wrappers over the service contracts; the
real orchestration lands in the application layer (Phase 2).
"""

from __future__ import annotations

from mcp.server.mcpserver import MCPServer

from hexa_sec.application.ports.driving.correlate.correlate_service_port import (
    CorrelateResult,
    CorrelateServicePort,
)
from hexa_sec.application.ports.driving.generate_report.generate_report_service_port import (
    GenerateReportResult,
    GenerateReportServicePort,
)
from hexa_sec.application.ports.driving.manage_mandate.manage_mandate_service_port import (
    ManageMandateResult,
    ManageMandateServicePort,
)
from hexa_sec.application.ports.driving.scan_asset.scan_asset_service_port import (
    ScanAssetResult,
    ScanAssetServicePort,
)
from hexa_sec.application.ports.driving.score_report.score_report_service_port import (
    ScoreReportResult,
    ScoreReportServicePort,
)


def scan_asset_handler(
    service: ScanAssetServicePort,
    asset: str,
    mandate_id: str,
    vendor: str,
    tenant_id: str,
    depth: str = "complete",
    exclusions: tuple[str, ...] = (),
) -> ScanAssetResult:
    return service.scan(
        {
            "asset": asset,
            "mandate_id": mandate_id,
            "vendor": vendor,
            "tenant_id": tenant_id,
            "depth": depth,
            "exclusions": exclusions,
        }
    )


def correlate_handler(service: CorrelateServicePort, scan_id: str) -> CorrelateResult:
    return service.correlate(
        {
            "scan_id": scan_id,
            "signals": (),
            "previous": (),
            "asset_criticalities": {},
            "exposure_open_ports": 3,
            "noise_count": 10,
        }
    )


def score_report_handler(service: ScoreReportServicePort, scan_id: str) -> ScoreReportResult:
    return service.score({"scan_id": scan_id, "items": ()})


def manage_mandate_handler(
    service: ManageMandateServicePort,
    client: str,
    targets: list[str],
    start_date: str,
    end_date: str,
    level: str,
) -> ManageMandateResult:
    return service.create(
        {
            "client": client,
            "targets": targets,
            "start_date": start_date,
            "end_date": end_date,
            "level": level,
        }
    )


def generate_report_handler(
    service: GenerateReportServicePort, scan_id: str
) -> GenerateReportResult:
    return service.generate({"scan_id": scan_id})


def build_server(
    scan_asset_svc: ScanAssetServicePort,
    correlate_svc: CorrelateServicePort,
    score_report_svc: ScoreReportServicePort,
    manage_mandate_svc: ManageMandateServicePort,
    generate_report_svc: GenerateReportServicePort,
) -> MCPServer:
    """Compose the MCP server with the 5 tools."""
    server = MCPServer(name="hexa-sec")

    @server.tool()
    def scan_asset(asset: str, mandate_id: str, vendor: str, tenant_id: str) -> ScanAssetResult:
        return scan_asset_handler(scan_asset_svc, asset, mandate_id, vendor, tenant_id)

    @server.tool()
    def correlate(scan_id: str) -> CorrelateResult:
        return correlate_handler(correlate_svc, scan_id)

    @server.tool()
    def score_report(scan_id: str) -> ScoreReportResult:
        return score_report_handler(score_report_svc, scan_id)

    @server.tool()
    def manage_mandate(
        client: str,
        targets: list[str],
        start_date: str,
        end_date: str,
        level: str,
    ) -> ManageMandateResult:
        return manage_mandate_handler(
            manage_mandate_svc, client, targets, start_date, end_date, level
        )

    @server.tool()
    def generate_report(scan_id: str) -> GenerateReportResult:
        return generate_report_handler(generate_report_svc, scan_id)

    return server
