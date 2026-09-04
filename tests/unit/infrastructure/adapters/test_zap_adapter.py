"""Tests for ZapAdapter (Dockerized web tool, approved image, no digest yet)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hexa_sec.application.ports.driven.execution_port import (
    ExecutionMetadata,
    ExecutionStatus,
    ToolExecutionRequest,
    ToolExecutionResult,
)
from hexa_sec.application.ports.driven.image_policy import ImageRef
from hexa_sec.domain.errors import ScannerTimeoutError, ScannerUnavailableError
from hexa_sec.infrastructure.adapters.secondary.scanners.web.zap_adapter import ZapAdapter

_REPO_ROOT = Path(__file__).resolve().parents[4]
_ZAP_FIXTURE = _REPO_ROOT / "datasets" / "zap_sample.json"


class _FakeExecution:
    def __init__(self, stdout: str) -> None:
        self._stdout = stdout
        self._request: ToolExecutionRequest | None = None

    def execute(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        self._request = request
        metadata = ExecutionMetadata(
            tool=request.tool,
            runtime="docker",
            image=request.image,
            status=ExecutionStatus.COMPLETED,
            exit_code=0,
            duration_ms=10,
            execution_id=request.execution_id,
            policy="deny-by-default",
        )
        return ToolExecutionResult(0, self._stdout, "", 10, ExecutionStatus.COMPLETED, request.execution_id, metadata)


class _FakeImagePolicy:
    def resolve(self, tool: str) -> ImageRef:
        return ImageRef(image="zaproxy/zap-stable", digest="sha256:zap")


class _NoImagePolicy:
    def resolve(self, tool: str) -> None:
        return None


class _RaisingExecution:
    def execute(self, request: ToolExecutionRequest) -> ToolExecutionResult:
        raise ScannerTimeoutError("zap execution timed out")


def test_zap_builds_request_and_parses_fixture() -> None:
    execution = _FakeExecution(_ZAP_FIXTURE.read_text(encoding="utf-8"))
    adapter = ZapAdapter(execution, _FakeImagePolicy())
    records = adapter.scan("https://app.acme.example")

    assert execution._request is not None
    assert execution._request.tool == "web_vuln_scan_zap"
    assert execution._request.digest == "sha256:zap"
    assert execution._request.command == "zap"
    assert execution._request.arguments[:2] == ("-u", "https://app.acme.example")
    assert len(records) == 2
    assert records[0]["title"] == "SQL Injection"
    assert records[0]["severity"] == "medium"
    assert records[0]["url"] == "https://app.acme.example/login"
    assert records[1]["severity"] == "low"


def test_zap_maps_riskcode_and_risk_labels() -> None:
    payload = {
        "site": [
            {
                "@name": "https://h",
                "alerts": [
                    {"alert": "a0", "riskcode": "0", "url": "https://h/0"},
                    {"alert": "a1", "riskcode": 1, "url": "https://h/1"},
                    {"alert": "a2", "riskcode": "2", "url": "https://h/2"},
                    {"alert": "a3", "riskcode": "3", "url": "https://h/3"},
                    {"alert": "b", "risk": "Informational", "url": "https://h/b"},
                    {"alert": "c", "risk": "Critical", "url": "https://h/c"},
                    {"alert": "d", "risk": "banana", "url": "https://h/d"},
                    {"alert": "e", "url": "https://h/e"},
                ],
            }
        ]
    }
    records = ZapAdapter(_FakeExecution(json.dumps(payload)), _FakeImagePolicy()).scan("https://h")
    assert [record["severity"] for record in records] == [
        "info",
        "low",
        "medium",
        "high",
        "info",
        "critical",
        "info",
        "info",
    ]


def test_zap_invalid_riskcode_falls_back_to_risk() -> None:
    payload = json.dumps(
        {"site": [{"@name": "https://h", "alerts": [{"alert": "x", "riskcode": "99", "risk": "High", "url": "https://h/x"}]}]}
    )
    records = ZapAdapter(_FakeExecution(payload), _FakeImagePolicy()).scan("https://h")
    assert records[0]["severity"] == "high"


def test_zap_blank_risk_and_blank_riskcode_fall_back_to_info() -> None:
    payload = json.dumps(
        {
            "site": [
                {
                    "@name": "https://h",
                    "alerts": [
                        {"alert": "a", "risk": "", "riskcode": "", "url": "https://h/a"},
                        {"alert": "b", "risk": "   ", "riskcode": "   ", "url": "https://h/b"},
                    ],
                }
            ]
        }
    )
    records = ZapAdapter(_FakeExecution(payload), _FakeImagePolicy()).scan("https://h")
    assert [record["severity"] for record in records] == ["info", "info"]


def test_zap_returns_empty_on_non_dict_root() -> None:
    assert ZapAdapter(_FakeExecution("[1,2]"), _FakeImagePolicy()).scan("https://h") == []


def test_zap_returns_empty_when_site_is_not_a_list() -> None:
    assert ZapAdapter(_FakeExecution('{"site": {"@name": "https://h"}}'), _FakeImagePolicy()).scan("https://h") == []


def test_zap_returns_empty_when_site_missing() -> None:
    assert ZapAdapter(_FakeExecution('{"@generated": "x"}'), _FakeImagePolicy()).scan("https://h") == []


def test_zap_returns_empty_on_empty_stdout() -> None:
    assert ZapAdapter(_FakeExecution(""), _FakeImagePolicy()).scan("https://h") == []


def test_zap_returns_empty_on_whitespace_stdout() -> None:
    assert ZapAdapter(_FakeExecution(" \n\t "), _FakeImagePolicy()).scan("https://h") == []


def test_zap_handles_invalid_json() -> None:
    assert ZapAdapter(_FakeExecution("not json"), _FakeImagePolicy()).scan("https://h") == []


def test_zap_skips_invalid_site_and_alert_items() -> None:
    payload = json.dumps(
        {
            "site": [
                "nope",
                {"@name": "https://h", "alerts": "not-a-list"},
                {
                    "@name": "https://h",
                    "alerts": [
                        42,
                        {"url": "https://h/no-title"},
                        {"alert": "no-url"},
                        {"alert": "", "url": "https://h/blank"},
                        {"alert": "ok", "url": "https://h/ok", "risk": "High"},
                    ],
                },
            ]
        }
    )
    records = ZapAdapter(_FakeExecution(payload), _FakeImagePolicy()).scan("https://h")
    assert len(records) == 1
    assert records[0]["title"] == "ok"


def test_zap_skips_blank_url() -> None:
    payload = json.dumps(
        {"site": [{"@name": "https://h", "alerts": [{"alert": "x", "url": "   "}]}]}
    )
    records = ZapAdapter(_FakeExecution(payload), _FakeImagePolicy()).scan("https://h")
    assert records == []


def test_zap_keeps_duplicates() -> None:
    payload = json.dumps(
        {
            "site": [
                {
                    "@name": "https://h",
                    "alerts": [
                        {"alert": "dup", "risk": "Low", "url": "https://h/1"},
                        {"alert": "dup", "risk": "Low", "url": "https://h/1"},
                    ],
                }
            ]
        }
    )
    records = ZapAdapter(_FakeExecution(payload), _FakeImagePolicy()).scan("https://h")
    assert len(records) == 2


def test_zap_raises_when_image_not_approved() -> None:
    adapter = ZapAdapter(_FakeExecution(""), _NoImagePolicy())
    with pytest.raises(ScannerUnavailableError) as excinfo:
        adapter.scan("https://h")
    assert "web_vuln_scan_zap image is not approved" in str(excinfo.value)


def test_zap_execution_error_propagates_unwrapped() -> None:
    """Error propagation: an execution failure (e.g. timeout) raised by the
    ToolExecutionPort must surface unchanged — the adapter never catches nor
    wraps what the execution layer already translated (ScannerTimeoutError)."""
    adapter = ZapAdapter(_RaisingExecution(), _FakeImagePolicy())
    with pytest.raises(ScannerTimeoutError) as excinfo:
        adapter.scan("https://h")
    assert "zap execution timed out" in str(excinfo.value)


def test_zap_parse_is_deterministic() -> None:
    """Stability/determinism: parsing is pure — identical input yields
    identical records across two runs (no ordering or hidden randomness)."""
    payload = _ZAP_FIXTURE.read_text(encoding="utf-8")
    execution = _FakeExecution(payload)
    adapter = ZapAdapter(execution, _FakeImagePolicy())
    first = adapter.scan("https://app.acme.example")
    second = adapter.scan("https://app.acme.example")
    assert first == second
    assert len(first) == 2
