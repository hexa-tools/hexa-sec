"""E2E — the full mocked flow: mandate → scan → correlate → report.

Mocks only. No real scanner, no network, no keys. Marked e2e (release CI
only), deselected from the default unit run.
"""

from __future__ import annotations

import pytest

from hexa_sec.adapters.primary.mcp_server import (
    correlate_handler,
    generate_report_handler,
    manage_mandate_handler,
    scan_asset_handler,
)
from hexa_sec.application.ports.driving.correlate.correlate_service_port import (
    CorrelateCommand,
    CorrelateResult,
)
from hexa_sec.application.ports.driving.generate_report.generate_report_service_port import (
    GenerateReportCommand,
    GenerateReportResult,
)
from hexa_sec.application.ports.driving.manage_mandate.manage_mandate_service_port import (
    ManageMandateCommand,
    ManageMandateResult,
)
from hexa_sec.application.ports.driving.scan_asset.scan_asset_service_port import (
    ScanAssetCommand,
    ScanAssetResult,
)
from hexa_sec.application.ports.driving.score_report.score_report_service_port import (
    ScoreReportCommand,
    ScoreReportResult,
    ScoreReportServicePort,
)


class FakeMandate:
    def create(self, command: ManageMandateCommand) -> ManageMandateResult:
        return {"mandate_id": "mnd_0001", "level": command["level"]}


class FakeScan:
    def scan(self, command: ScanAssetCommand) -> ScanAssetResult:
        return {"scan_id": "scan_0001", "status": "done"}


class FakeScore(ScoreReportServicePort):
    def score(self, command: ScoreReportCommand) -> ScoreReportResult:
        return {"scan_id": command["scan_id"], "score": 62, "label": "moderate"}


class FakeCorrelate:
    def correlate(self, command: CorrelateCommand) -> CorrelateResult:
        return {"scan_id": command["scan_id"], "correlations": [{"type": "attack-chain"}]}


class FakeReport:
    def generate(self, command: GenerateReportCommand) -> GenerateReportResult:
        return {"report_id": "rep_0001", "markdown": "# Audit report\n62/100 moderate\n"}


@pytest.mark.e2e
def test_full_mocked_flow() -> None:
    mandate = manage_mandate_handler(
        FakeMandate(),
        "Acme",
        ["10.0.0.1"],
        "2026-01-01",
        "2026-12-31",
        "standard",
        signature="REF-2026-0001",
        actor="operator",
        tenant_id="tnt_0001",
    )
    assert mandate["mandate_id"] == "mnd_0001"

    scan = scan_asset_handler(
        FakeScan(),
        asset="10.0.0.1",
        mandate_id=mandate["mandate_id"],
        vendor="nessus",
        tenant_id="tnt_0001",
    )
    assert scan["status"] == "done"

    score = FakeScore().score({"scan_id": scan["scan_id"]})
    assert score["score"] == 62

    correlate = correlate_handler(FakeCorrelate(), scan_id=scan["scan_id"])
    assert correlate["correlations"][0]["type"] == "attack-chain"

    report = generate_report_handler(FakeReport(), scan_id=scan["scan_id"])
    assert "moderate" in report["markdown"]
