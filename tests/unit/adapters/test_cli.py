"""Tests for the hexa-sec CLI (primary adapter)."""

from __future__ import annotations

from click.testing import CliRunner

from hexa_sec.adapters.primary.cli import build_cli


def test_cli_exposes_four_commands() -> None:
    cli = build_cli()
    assert set(cli.commands) == {"scan", "correlate", "report", "mandate"}


def test_cli_scan_command_routes_through_use_case() -> None:
    runner = CliRunner()
    result = runner.invoke(build_cli(), ["scan", "--asset", "10.0.0.1", "--mandate-id", "mnd_0001"])
    assert result.exception is not None


def test_cli_correlate_command_routes_through_use_case() -> None:
    runner = CliRunner()
    result = runner.invoke(build_cli(), ["correlate", "--scan-id", "scan_0001"])
    assert result.exception is None
    assert result.exit_code == 0


def test_cli_report_command_routes_through_use_case() -> None:
    runner = CliRunner()
    result = runner.invoke(build_cli(), ["report", "--scan-id", "scan_0001"])
    assert result.exception is not None


def test_cli_mandate_command_routes_through_use_case() -> None:
    runner = CliRunner()
    result = runner.invoke(
        build_cli(),
        ["mandate", "--client", "Acme", "--target", "10.0.0.1", "--start", "2026-01-01", "--end", "2026-12-31"],
    )
    assert result.exception is not None
