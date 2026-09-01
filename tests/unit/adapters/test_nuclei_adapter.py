"""Tests for NucleiAdapter (Dockerized web tool)."""

from __future__ import annotations

import json

from hexa_sec.adapters.secondary.scanners.web.nuclei_adapter import NucleiAdapter
from hexa_sec.application.ports.driven.execution_port import (
    ExecutionMetadata,
    ExecutionStatus,
    ToolExecutionRequest,
    ToolExecutionResult,
)
from hexa_sec.application.ports.driven.image_policy import ImageRef


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
        return ImageRef(image="projectdiscovery/nuclei")


def test_nuclei_builds_request_and_parses_json() -> None:
    payload = json.dumps([{"host": "app.example", "info": {"severity": "critical", "name": "RCE"}}])
    execution = _FakeExecution(payload)
    adapter = NucleiAdapter(execution, _FakeImagePolicy())
    records = adapter.scan("https://app.example")
    assert execution._request is not None
    assert execution._request.command == "nuclei"
    assert records[0]["url"] == "app.example"
    assert records[0]["severity"] == "critical"


def test_nuclei_returns_empty_on_no_matches() -> None:
    execution = _FakeExecution("")
    assert NucleiAdapter(execution, _FakeImagePolicy()).scan("https://app.example") == []


def test_nuclei_handles_invalid_json() -> None:
    execution = _FakeExecution("not json")
    assert NucleiAdapter(execution, _FakeImagePolicy()).scan("https://app.example") == []


def test_nuclei_ignores_non_dict_items() -> None:
    execution = _FakeExecution(json.dumps(["nope", {"host": "app.example", "info": {"name": "x"}}]))
    records = NucleiAdapter(execution, _FakeImagePolicy()).scan("https://app.example")
    assert len(records) == 1
