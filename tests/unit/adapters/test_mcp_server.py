"""Tests for the MCP server (entrypoint mcp://)."""

from __future__ import annotations

import asyncio

from hexa_sec.adapters.primary.mcp_server import build_server, scan_asset_handler

from hexa_sec.application.ports.driving.scan_asset.scan_asset_service_port import ScanAssetCommand


class _FakeScanAssetService:
    def scan(self, command: ScanAssetCommand) -> dict[str, str]:
        return {"scan_id": command["mandate_id"], "status": "pending"}


def test_build_server_registers_five_tools() -> None:
    server = build_server(
        scan_asset_svc=_FakeScanAssetService(),
        correlate_svc=object(),
        score_report_svc=object(),
        manage_mandate_svc=object(),
        generate_report_svc=object(),
    )
    tools = asyncio.run(server.list_tools())
    names = sorted(tool.name for tool in tools)
    assert names == ["correlate", "generate_report", "manage_mandate", "scan_asset", "score_report"]


def test_scan_asset_handler_delegates() -> None:
    service = _FakeScanAssetService()
    result = scan_asset_handler(service, asset="10.0.0.1", mandate_id="mnd_0001", vendor="nessus")
    assert result["status"] == "pending"
