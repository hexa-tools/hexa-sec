"""Tests for the tool execution port contract (Docker runtime bootstrap)."""

from __future__ import annotations

import inspect

import pytest

from hexa_sec.application.ports.driven.execution_port import (
    ExecutionMetadata,
    ExecutionStatus,
    Mount,
    ResourceLimits,
    ToolExecutionPort,
    ToolExecutionRequest,
    ToolExecutionResult,
)


def test_execution_status_members() -> None:
    assert ExecutionStatus.COMPLETED.value == "completed"
    assert ExecutionStatus.TIMED_OUT.value == "timed_out"
    assert ExecutionStatus.FAILED.value == "failed"


def test_mount_creation() -> None:
    mount = Mount(source="/input", destination="/work", read_only=True)
    assert mount.read_only is True
    assert mount.destination == "/work"


def test_mount_rejects_empty_source() -> None:
    with pytest.raises(ValueError):
        Mount(source="", destination="/work")


def test_mount_rejects_empty_destination() -> None:
    with pytest.raises(ValueError):
        Mount(source="/input", destination=" ")


def test_resource_limits_defaults_none() -> None:
    limits = ResourceLimits()
    assert limits.cpu is None
    assert limits.memory_mb is None
    assert limits.pids is None
    assert limits.disk_mb is None


def test_resource_limits_rejects_negative() -> None:
    with pytest.raises(ValueError):
        ResourceLimits(cpu=-1.0, memory_mb=512, pids=200, disk_mb=100)


def test_tool_request_defaults_deny_network() -> None:
    request = ToolExecutionRequest(image="nmap:7", command="nmap")
    assert request.network == "none"
    assert request.mounts == ()
    assert request.resources is None


def test_tool_request_carries_args_and_env() -> None:
    request = ToolExecutionRequest(
        image="nmap:7",
        command="nmap",
        arguments=("-sV", "10.0.0.1"),
        environment={"TARGET": "10.0.0.1"},
        timeout=30.0,
    )
    assert request.arguments == ("-sV", "10.0.0.1")
    assert request.environment == {"TARGET": "10.0.0.1"}
    assert request.timeout == 30.0


def test_tool_execution_result_creation() -> None:
    metadata = ExecutionMetadata(
        tool="network_port_discovery",
        runtime="docker",
        image="nmap:7",
        status=ExecutionStatus.COMPLETED,
        exit_code=0,
        duration_ms=1842,
        execution_id="exec_0001",
        policy="default",
    )
    result = ToolExecutionResult(
        exit_code=0,
        stdout="PORT STATE",
        stderr="",
        duration_ms=1842,
        status=ExecutionStatus.COMPLETED,
        execution_id="exec_0001",
        metadata=metadata,
    )
    assert result.metadata.image == "nmap:7"
    assert result.status is ExecutionStatus.COMPLETED


def test_tool_execution_port_is_abstract() -> None:
    assert inspect.isabstract(ToolExecutionPort) is True
