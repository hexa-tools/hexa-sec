"""Integration — a real ephemeral Docker container, removed after execution.

Requires a running Docker daemon; skips otherwise so unit/coverage gates stay
green without Docker. CI runs it in a Docker-enabled job.
"""

from __future__ import annotations

import shutil

import pytest

from hexa_sec.adapters.secondary.execution.docker_command_runner import CliDockerCommandRunner
from hexa_sec.adapters.secondary.execution.docker_runtime import DockerRuntime
from hexa_sec.application.ports.driven.execution_port import ExecutionStatus, ToolExecutionRequest


def _docker_available() -> bool:
    return shutil.which("docker") is not None


@pytest.mark.integration
def test_ephemeral_container_runs_and_is_removed() -> None:
    if not _docker_available():
        pytest.skip("docker not available")
    runner = CliDockerCommandRunner()
    runtime = DockerRuntime(runner)
    request = ToolExecutionRequest(
        image="alpine",
        digest="sha256:28bd5fe8b56d1bd048e5babf5b10710ebe0bae67db86916198a6eec434943f8b",
        command="echo",
        arguments=("hello",),
        network="none",
        timeout=30.0,
        execution_id="integration-1",
    )
    result = runtime.execute(request)
    # the container name is derived from the execution id
    leftover = runner.run(["ps", "-a", "--filter", "name=hexa-sec-integration-1", "--format", "{{.ID}}"])
    assert result.status is ExecutionStatus.COMPLETED
    assert "hello" in result.stdout
    assert leftover.stdout.strip() == ""
