"""Tests for the CLI Docker command runner (Docker runtime bootstrap)."""

from __future__ import annotations

import subprocess

import pytest

from hexa_sec.adapters.secondary.execution.docker_command_runner import (
    CliDockerCommandRunner,
    CommandResult,
    _text,
)


def test_cli_runner_executes_argv(capsys: pytest.CaptureFixture[str]) -> None:
    runner = CliDockerCommandRunner()
    result = runner.run(["printf", "hello"])
    assert result.returncode == 0


def test_cli_runner_captures_output() -> None:
    runner = CliDockerCommandRunner()
    result = runner.run(["printf", "PORT STATE"])
    assert "PORT STATE" in result.stdout
    assert result.timed_out is False


def test_cli_runner_reports_nonzero_exit() -> None:
    runner = CliDockerCommandRunner()
    result = runner.run(["python", "-c", "import sys; sys.exit(3)"])
    assert result.returncode == 3
    assert result.timed_out is False


def test_cli_runner_marks_timeout() -> None:
    runner = CliDockerCommandRunner()
    result = runner.run(["sleep", "5"], timeout=0.05)
    assert result.timed_out is True
    assert result.returncode != 0


def test_command_result_fields() -> None:
    result = CommandResult(returncode=1, stdout="", stderr="boom", timed_out=True)
    assert result.stderr == "boom"
    assert result.timed_out is True


def test_text_coerces_bytes_and_none() -> None:
    assert _text(b"hello") == "hello"
    assert _text("world") == "world"
    assert _text(None) == ""
