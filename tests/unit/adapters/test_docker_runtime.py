"""Tests for the Docker runtime — behavior-first, mock the command runner."""

from __future__ import annotations

from pathlib import Path

import pytest

from hexa_sec.adapters.secondary.execution.docker_command_runner import CommandResult
from hexa_sec.adapters.secondary.execution.docker_runtime import DockerRuntime
from hexa_sec.application.ports.driven.execution_port import (
    ExecutionStatus,
    Mount,
    ResourceLimits,
    ToolExecutionRequest,
)
from hexa_sec.domain.errors import ScannerUnavailableError, SecurityPolicyError


class _FakeRunner:
    def __init__(
        self,
        wait_timed_out: bool = False,
        wait_rc: int = 0,
        container_id: str = "ctr-1",
        inspect_rc: int = 0,
        run_rc: int = 0,
        pull_rc: int = 0,
    ) -> None:
        self.calls: list[tuple[list[str], float | None]] = []
        self.wait_timed_out = wait_timed_out
        self.wait_rc = wait_rc
        self.container_id = container_id
        self.inspect_rc = inspect_rc
        self.run_rc = run_rc
        self.pull_rc = pull_rc
        self.fail_on: str | None = None

    def run(self, command: list[str], timeout: float | None = None) -> CommandResult:
        self.calls.append((list(command), timeout))
        if self.fail_on is not None and self.fail_on in command:
            raise RuntimeError(f"boom on {command}")
        sub = command[1] if len(command) > 1 and command[0] == "docker" else (command[0] if command else "")
        if sub == "run":
            return CommandResult(self.run_rc, self.container_id, "")
        if sub == "wait":
            return CommandResult(self.wait_rc, "", "", timed_out=self.wait_timed_out)
        if sub == "logs":
            return CommandResult(0, "PORT   STATE\n80/tcp open", "")
        if sub == "image":
            return CommandResult(self.inspect_rc, "", "")
        if sub == "pull":
            return CommandResult(self.pull_rc, "", "")
        return CommandResult(0, "", "")


def _request(**overrides: object) -> ToolExecutionRequest:
    defaults: dict[str, object] = {
        "image": "instrumentisto/nmap",
        "digest": "sha256:abc",
        "command": "nmap",
        "arguments": ("-sV", "10.0.0.1"),
        "network": "none",
        "resources": ResourceLimits(memory_mb=512, pids=200, cpu=1.0),
        "timeout": 60.0,
        "execution_id": "exec-1",
    }
    defaults.update(overrides)
    return ToolExecutionRequest(**defaults)


def test_execute_refuses_without_digest() -> None:
    # deny-by-default : pas de tag glissant, une image sans digest est refusée
    with pytest.raises(SecurityPolicyError):
        DockerRuntime(_FakeRunner()).execute(_request(digest=None))


def test_execute_pulls_by_image_at_digest() -> None:
    runner = _FakeRunner(inspect_rc=1)
    DockerRuntime(runner).execute(_request())
    pull = next(cmd for cmd, _ in runner.calls if cmd[:2] == ["docker", "pull"])
    assert "instrumentisto/nmap@sha256:abc" in pull


def test_metadata_image_is_digest_ref() -> None:
    result = DockerRuntime(_FakeRunner()).execute(_request())
    assert result.metadata.image == "instrumentisto/nmap@sha256:abc"


def test_execute_success_and_cleanup() -> None:
    runner = _FakeRunner()
    result = DockerRuntime(runner).execute(_request())
    assert result.status is ExecutionStatus.COMPLETED
    assert result.exit_code == 0
    assert "80/tcp open" in result.stdout
    assert any(cmd[0] == "docker" and "rm" in cmd and "-f" in cmd and "ctr-1" in cmd for cmd, _ in runner.calls)
    assert any(cmd[0] == "docker" and "run" in cmd and "--memory" in cmd and "512m" in cmd for cmd, _ in runner.calls)


def test_execute_reports_failure_on_nonzero_exit() -> None:
    runner = _FakeRunner(wait_rc=2)
    result = DockerRuntime(runner).execute(_request())
    assert result.status is ExecutionStatus.FAILED
    assert result.exit_code == 2


def test_execute_times_out_and_cleans_up() -> None:
    runner = _FakeRunner(wait_timed_out=True)
    result = DockerRuntime(runner).execute(_request(timeout=5.0))
    assert result.status is ExecutionStatus.TIMED_OUT
    assert any(cmd[0] == "docker" and "kill" in cmd for cmd, _ in runner.calls)
    assert any(cmd[0] == "docker" and "rm" in cmd and "-f" in cmd and "ctr-1" in cmd for cmd, _ in runner.calls)


def test_cleanup_runs_even_when_logs_fail() -> None:
    runner = _FakeRunner()
    runner.fail_on = "logs"
    with pytest.raises(RuntimeError):
        DockerRuntime(runner).execute(_request())
    assert any(cmd[0] == "docker" and "rm" in cmd and "-f" in cmd and "ctr-1" in cmd for cmd, _ in runner.calls)


def test_command_is_argv_not_shell_concatenation() -> None:
    runner = _FakeRunner()
    DockerRuntime(runner).execute(_request())
    run_call = next(cmd for cmd, _ in runner.calls if cmd[:2] == ["docker", "run"])
    assert "nmap" in run_call
    assert "-sV" in run_call
    assert "10.0.0.1" in run_call


def test_network_is_disabled_by_default() -> None:
    runner = _FakeRunner()
    DockerRuntime(runner).execute(_request())
    run_call = next(cmd for cmd, _ in runner.calls if cmd[:2] == ["docker", "run"])
    assert "--network" in run_call
    assert run_call[run_call.index("--network") + 1] == "none"


def test_host_network_denied() -> None:
    with pytest.raises(SecurityPolicyError):
        DockerRuntime(_FakeRunner()).execute(_request(network="host"))


def test_docker_socket_mount_denied() -> None:
    request = _request(mounts=(Mount(source="/var/run/docker.sock", destination="/var/run/docker.sock"),))
    with pytest.raises(SecurityPolicyError):
        DockerRuntime(_FakeRunner()).execute(request)


def test_host_secret_path_mount_denied() -> None:
    secret = str(Path.home() / ".ssh")
    request = _request(mounts=(Mount(source=secret, destination="/root/.ssh"),))
    with pytest.raises(SecurityPolicyError):
        DockerRuntime(_FakeRunner()).execute(request)


def test_image_pulled_when_not_present() -> None:
    runner = _FakeRunner(inspect_rc=1)
    DockerRuntime(runner).execute(_request())
    assert any(cmd[:2] == ["docker", "pull"] for cmd, _ in runner.calls)


def test_pull_failure_raises_scanner_error() -> None:
    # catégorie « erreur & propagation » : un pull échoué -> ScannerUnavailableError
    # (jamais un :latest glissant, jamais une erreur brute).
    with pytest.raises(ScannerUnavailableError):
        DockerRuntime(_FakeRunner(inspect_rc=1, pull_rc=1)).execute(_request())


def test_container_start_failure_raises() -> None:
    runner = _FakeRunner(run_rc=1)
    with pytest.raises(SecurityPolicyError):
        DockerRuntime(runner).execute(_request())


def test_lifecycle_order_and_cleanup_is_last() -> None:
    # catégorie « concurrence / ordre » : le cycle de vie est strictement
    # ordonné et le cleanup est TOUJOURS le dernier appel (pas d'orphelin).
    runner = _FakeRunner()
    DockerRuntime(runner).execute(_request())
    subs = [cmd[1] if len(cmd) > 1 else cmd[0] for cmd, _ in runner.calls]
    assert subs.index("run") < subs.index("wait")
    assert subs.index("wait") < subs.index("logs")
    assert subs.index("logs") < subs.index("rm")
    assert subs[-1] == "rm"


def test_execution_deterministic_parts_are_reproducible() -> None:
    # catégorie « déterminisme » : status/exit_code/stdout sont reproductibles
    # entre deux exécutions identiques (seul duration varie, par conception).
    first = DockerRuntime(_FakeRunner()).execute(_request())
    second = DockerRuntime(_FakeRunner()).execute(_request())
    assert first.status is second.status
    assert first.exit_code == second.exit_code
    assert first.stdout == second.stdout
    assert first.metadata.image == second.metadata.image


def test_env_and_readonly_mount_flags_present() -> None:
    runner = _FakeRunner()
    request = _request(
        environment={"TARGET": "10.0.0.1"},
        mounts=(Mount(source="/input", destination="/work", read_only=True),),
        resources=ResourceLimits(cpu=0.5, pids=100, memory_mb=256, disk_mb=1024),
    )
    DockerRuntime(runner).execute(request)
    run_call = next(cmd for cmd, _ in runner.calls if cmd[:2] == ["docker", "run"])
    assert "-e" in run_call and "TARGET=10.0.0.1" in run_call
    assert any("readonly" in flag for flag in run_call)
    assert "--cpus" in run_call and "0.5" in run_call
    assert "--pids-limit" in run_call and "100" in run_call


def test_disk_and_rw_mount_flags_present() -> None:
    runner = _FakeRunner()
    request = _request(
        resources=ResourceLimits(memory_mb=512, pids=200, cpu=1.0, disk_mb=2048),
        mounts=(Mount(source="/input", destination="/work"),),
        network="bridge",
    )
    DockerRuntime(runner).execute(request)
    run_call = next(cmd for cmd, _ in runner.calls if cmd[:2] == ["docker", "run"])
    assert "--storage-opt" in run_call
    assert "size=2048M" in run_call
    assert any("src=/input,dst=/work,rw" in flag for flag in run_call)
