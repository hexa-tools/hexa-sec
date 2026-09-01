"""Tests for the hexa_guard rules (R1-R8 family)."""

from __future__ import annotations

from hexa_guard import find_violations


def test_domain_purity_sdk_flagged() -> None:
    violations = find_violations("src/hexa_sec/domain/asset/asset.py", "import requests")
    assert any(v.startswith("R1") for v in violations)


def test_clean_domain_has_no_violations() -> None:
    violations = find_violations(
        "src/hexa_sec/domain/asset/asset.py",
        "from dataclasses import dataclass\nclass A:\n    pass\n",
    )
    assert violations == []


def test_adapter_importing_domain_flagged() -> None:
    violations = find_violations(
        "src/hexa_sec/adapters/primary/cli.py",
        "from hexa_sec.domain.asset.asset import Asset\n",
    )
    assert any(v.startswith("R2") for v in violations)


def test_inline_sql_flagged() -> None:
    violations = find_violations("src/hexa_sec/x/repo.py", 'cur.execute("SELECT * FROM reports")')
    assert any(v.startswith("R4") for v in violations)


def test_secret_pattern_flagged() -> None:
    violations = find_violations("src/hexa_sec/adapters/secondary/nvd.py", 'api_key = "sk-1234567890abcdef123456"')
    assert any(v.startswith("R3") for v in violations)


def test_bare_annotation_flagged() -> None:
    violations = find_violations("src/hexa_sec/application/service/s.py", "def foo() -> dict:\n    pass\n")
    assert any(v.startswith("R5") for v in violations)


def test_try_except_in_service_flagged() -> None:
    violations = find_violations(
        "src/hexa_sec/application/service/scan_asset_service.py",
        "try:\n    pass\nexcept Exception:\n    pass\n",
    )
    assert any(v.startswith("R6") for v in violations)


def test_docker_in_adapter_outside_execution_flagged() -> None:
    violations = find_violations(
        "src/hexa_sec/adapters/secondary/scanners/network/nmap_adapter.py",
        'subprocess.run(["docker", "run", "-d", image])',
    )
    assert any(v.startswith("R9") for v in violations)


def test_generic_raise_in_service_flagged() -> None:
    violations = find_violations(
        "src/hexa_sec/application/service/scan_asset_service.py",
        "raise ValueError('boom')\n",
    )
    assert any(v.startswith("R6") for v in violations)


def test_driving_port_bad_filename_flagged() -> None:
    violations = find_violations(
        "src/hexa_sec/application/ports/driving/correlate/bad_name.py",
        "def go() -> None:\n    pass\n",
    )
    assert any(v.startswith("R10") for v in violations)


def test_select_star_in_memory_flagged() -> None:
    violations = find_violations(
        "src/hexa_sec/infrastructure/memory/report_repository.py",
        'cursor.execute("SELECT * FROM reports")',
    )
    assert any(v.startswith("R11") for v in violations)


def test_mutation_in_readonly_layer_flagged() -> None:
    violations = find_violations(
        "src/hexa_sec/application/ports/driving/mcp_server.py",
        "kubectl delete ns production",
    )
    assert any(v.startswith("R14") for v in violations)
