"""Tests for the MCP server (entrypoint mcp://)."""

from __future__ import annotations

import asyncio

from hexa_sec.adapters.primary.mcp_server import build_server, scan_asset_handler

from hexa_sec.application.ports.driving.scan_asset.scan_asset_service_port import ScanAssetCommand


class _FakeScanAsset:
    def scan(self, command: ScanAssetCommand) -> dict[str, object]:
        return {
            "scan_id": command["mandate_id"],
            "status": "pending",
            "mandate_id": command["mandate_id"],
            "findings": [],
        }


class _FakeCorrelate:
    def correlate(self, command: dict[str, str]) -> dict[str, object]:
        return {"scan_id": command["scan_id"], "correlations": []}


class _FakeScore:
    def score(self, command: dict[str, str]) -> dict[str, object]:
        return {
            "scan_id": command["scan_id"],
            "score": 62,
            "label": "moderate",
            "ordered": (),
        }


class _FakeMandate:
    def create(self, command: dict[str, object]) -> dict[str, str]:
        return {"mandate_id": "mnd_0001", "level": str(command["level"])}


class _FakeReport:
    def generate(self, command: dict[str, str]) -> dict[str, str]:
        return {"report_id": "rep_0001", "markdown": "# report"}


def _server() -> object:
    return build_server(
        scan_asset_svc=_FakeScanAsset(),
        correlate_svc=_FakeCorrelate(),
        score_report_svc=_FakeScore(),
        manage_mandate_svc=_FakeMandate(),
        generate_report_svc=_FakeReport(),
    )


def test_build_server_registers_five_tools() -> None:
    tools = asyncio.run(_server().list_tools())
    names = sorted(tool.name for tool in tools)
    assert names == ["correlate", "generate_report", "manage_mandate", "scan_asset", "score_report"]


def test_scan_asset_handler_delegates() -> None:
    result = scan_asset_handler(
        _FakeScanAsset(),
        asset="10.0.0.1",
        mandate_id="mnd_0001",
        vendor="nessus",
        tenant_id="tnt_0001",
    )
    assert result["status"] == "pending"


def test_scan_asset_tool_via_call_tool() -> None:
    server = _server()
    result = asyncio.run(
        server.call_tool(
            "scan_asset",
            {
                "asset": "10.0.0.1",
                "mandate_id": "mnd_0001",
                "vendor": "nessus",
                "tenant_id": "tnt_0001",
            },
        )
    )
    assert result.is_error is False


def test_correlate_tool_via_call_tool() -> None:
    server = _server()
    result = asyncio.run(server.call_tool("correlate", {"scan_id": "scan_0001"}))
    assert result.is_error is False


def test_score_report_tool_via_call_tool() -> None:
    server = _server()
    result = asyncio.run(server.call_tool("score_report", {"scan_id": "scan_0001"}))
    assert result.is_error is False


def test_manage_mandate_tool_via_call_tool() -> None:
    server = _server()
    result = asyncio.run(
        server.call_tool(
            "manage_mandate",
            {
                "client": "Acme",
                "targets": ["10.0.0.1"],
                "start_date": "2026-01-01",
                "end_date": "2026-12-31",
                "level": "standard",
                "signature": "REF-2026-0001",
                "actor": "operator",
                "tenant_id": "tnt_0001",
            },
        )
    )
    assert result.is_error is False


def test_generate_report_tool_via_call_tool() -> None:
    server = _server()
    result = asyncio.run(server.call_tool("generate_report", {"scan_id": "scan_0001"}))
    assert result.is_error is False
