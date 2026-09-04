"""Tests for BurpAdapter (Dockerized web tool, deny-by-default image)."""

from __future__ import annotations

import json

import pytest

from hexa_sec.application.ports.driven.execution_port import (
    ExecutionMetadata,
    ExecutionStatus,
    ToolExecutionRequest,
    ToolExecutionResult,
)
from hexa_sec.application.ports.driven.image_policy import ImageRef
from hexa_sec.domain.errors import ScannerUnavailableError
from hexa_sec.infrastructure.adapters.secondary.scanners.web.burp_adapter import BurpAdapter

_BURP_ISSUES = {
    "issues": [
        {
            "name": "SQL injection",
            "host": "https://app.acme.example",
            "path": "/login",
            "severity": "high",
            "confidence": "certain",
        },
        {
            "name": "Missing security headers",
            "host": "https://app.acme.example",
            "path": "/",
            "severity": "low",
            "confidence": "certain",
        },
    ]
}


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
        return ImageRef(image="portswigger/burp", digest="sha256:burp")


class _NoImagePolicy:
    def resolve(self, tool: str) -> None:
        return None


def test_burp_builds_request_and_parses_issues() -> None:
    execution = _FakeExecution(json.dumps(_BURP_ISSUES))
    adapter = BurpAdapter(execution, _FakeImagePolicy())
    records = adapter.scan("https://app.acme.example")

    assert execution._request is not None
    assert execution._request.tool == "web_vuln_scan_burp"
    assert execution._request.digest == "sha256:burp"
    assert execution._request.command == "burp"
    assert execution._request.arguments[:2] == ("-u", "https://app.acme.example")
    assert len(records) == 2
    assert records[0]["title"] == "SQL injection"
    assert records[0]["severity"] == "high"
    assert records[0]["url"] == "https://app.acme.example/login"
    assert records[1]["severity"] == "low"


def test_burp_maps_severity_vocabulary() -> None:
    payload = {
        "issues": [
            {"name": "a", "host": "https://h", "severity": "critical"},
            {"name": "b", "host": "https://h", "severity": "Information"},
            {"name": "c", "host": "https://h", "severity": "MEDIUM"},
            {"name": "d", "host": "https://h", "severity": "banana"},
            {"name": "e", "host": "https://h"},
        ]
    }
    records = BurpAdapter(_FakeExecution(json.dumps(payload)), _FakeImagePolicy()).scan("https://h")
    assert [record["severity"] for record in records] == ["critical", "info", "medium", "info", "info"]


def test_burp_root_as_list_is_parsed() -> None:
    payload = json.dumps([{"name": "x", "host": "https://h", "path": "/a", "severity": "medium"}])
    records = BurpAdapter(_FakeExecution(payload), _FakeImagePolicy()).scan("https://h")
    assert len(records) == 1
    assert records[0]["url"] == "https://h/a"


def test_burp_missing_path_uses_host_as_url() -> None:
    payload = json.dumps({"issues": [{"name": "x", "host": "https://h", "severity": "low"}]})
    records = BurpAdapter(_FakeExecution(payload), _FakeImagePolicy()).scan("https://h")
    assert records[0]["url"] == "https://h"


def test_burp_returns_empty_on_no_issues_field() -> None:
    records = BurpAdapter(_FakeExecution('{"report": "ok"}'), _FakeImagePolicy()).scan("https://h")
    assert records == []


def test_burp_returns_empty_when_issues_is_not_a_list() -> None:
    records = BurpAdapter(_FakeExecution('{"issues": {"name": "x"}}'), _FakeImagePolicy()).scan("https://h")
    assert records == []


def test_burp_returns_empty_on_root_that_is_not_object_or_list() -> None:
    assert BurpAdapter(_FakeExecution("42"), _FakeImagePolicy()).scan("https://h") == []


def test_burp_returns_empty_on_empty_stdout() -> None:
    assert BurpAdapter(_FakeExecution(""), _FakeImagePolicy()).scan("https://h") == []


def test_burp_returns_empty_on_whitespace_stdout() -> None:
    assert BurpAdapter(_FakeExecution(" \n\t "), _FakeImagePolicy()).scan("https://h") == []


def test_burp_handles_invalid_json() -> None:
    assert BurpAdapter(_FakeExecution("not json"), _FakeImagePolicy()).scan("https://h") == []


def test_burp_ignores_non_dict_and_incomplete_items() -> None:
    payload = json.dumps(
        {
            "issues": [
                "nope",
                42,
                {"name": "missing-host"},
                {"host": "https://h"},
                {"name": "", "host": "https://h"},
                {"name": "   ", "host": "https://h"},
                {"name": "ok", "host": "https://h", "severity": "high"},
            ]
        }
    )
    records = BurpAdapter(_FakeExecution(payload), _FakeImagePolicy()).scan("https://h")
    assert len(records) == 1
    assert records[0]["title"] == "ok"


def test_burp_keeps_duplicates() -> None:
    payload = json.dumps(
        {
            "issues": [
                {"name": "dup", "host": "https://h", "severity": "low"},
                {"name": "dup", "host": "https://h", "severity": "low"},
            ]
        }
    )
    records = BurpAdapter(_FakeExecution(payload), _FakeImagePolicy()).scan("https://h")
    assert len(records) == 2


def test_burp_raises_when_image_not_approved() -> None:
    adapter = BurpAdapter(_FakeExecution(""), _NoImagePolicy())
    with pytest.raises(ScannerUnavailableError) as excinfo:
        adapter.scan("https://h")
    assert "web_vuln_scan_burp image is not approved" in str(excinfo.value)


def test_burp_skips_item_with_blank_or_whitespace_host() -> None:
    """Absence/empty boundary: a present-but-blank host ('', whitespace) is
    skipped — it must never produce an evidence-less finding with empty url."""
    payload = json.dumps(
        {
            "issues": [
                {"name": "no-host", "host": ""},
                {"name": "ws-host", "host": "   "},
                {"name": "ok", "host": "https://h", "severity": "low"},
            ]
        }
    )
    records = BurpAdapter(_FakeExecution(payload), _FakeImagePolicy()).scan("https://h")
    assert len(records) == 1
    assert records[0]["title"] == "ok"


def test_burp_blank_path_keeps_host_as_url() -> None:
    """Boundary presence/absence: a blank path string ('', ' ') must not be
    concatenated ('host ' or 'host   ') — the url stays exactly the host."""
    payload = json.dumps(
        {
            "issues": [
                {"name": "a", "host": "https://h", "path": ""},
                {"name": "b", "host": "https://h", "path": "   "},
            ]
        }
    )
    records = BurpAdapter(_FakeExecution(payload), _FakeImagePolicy()).scan("https://h")
    assert [record["url"] for record in records] == ["https://h", "https://h"]


def test_burp_blank_severity_maps_to_info() -> None:
    """Absence must not masquerade as a level: an empty or whitespace severity
    string follows the missing-severity rule (info), never an invented level."""
    payload = json.dumps(
        {
            "issues": [
                {"name": "a", "host": "https://h", "severity": ""},
                {"name": "b", "host": "https://h", "severity": "   "},
            ]
        }
    )
    records = BurpAdapter(_FakeExecution(payload), _FakeImagePolicy()).scan("https://h")
    assert [record["severity"] for record in records] == ["info", "info"]


def test_burp_parse_is_deterministic() -> None:
    """Stability/determinism: parsing is pure — two runs on identical input
    must yield identical records (no ordering or hidden randomness)."""
    execution = _FakeExecution(json.dumps(_BURP_ISSUES))
    adapter = BurpAdapter(execution, _FakeImagePolicy())
    first = adapter.scan("https://app.acme.example")
    second = adapter.scan("https://app.acme.example")
    assert first == second
    assert len(first) == 2
