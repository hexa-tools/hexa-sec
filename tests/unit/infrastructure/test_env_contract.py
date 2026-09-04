"""Tests for the .env contract validator (SEC-2)."""

from __future__ import annotations

from pathlib import Path

import pytest

from hexa_sec.infrastructure.config.env_contract import (
    KeySpec,
    main,
    parse_env,
    parse_template,
    validate_env,
    validate_template,
)

TEMPLATE = (
    "## HEXA-SEC\n"
    "SHODAN_API_KEY=   # Shodan (exposition Internet)\n"
    "HEXA_SEC_MCP_TOKEN=   # token MCP  # REQUIRED\n"
    "## HEXA-CLOUD\n"
    "DATABASE_URL=   # PostgreSQL  # REQUIRED\n"
)


def test_parse_template_captures_sections_keys_and_required() -> None:
    specs = parse_template(TEMPLATE)
    assert [s.key for s in specs] == ["SHODAN_API_KEY", "HEXA_SEC_MCP_TOKEN", "DATABASE_URL"]
    assert specs[2].section == "HEXA-CLOUD"
    assert specs[1].required is True
    assert specs[2].required is True
    assert specs[0].required is False


def test_parse_template_defaults_keys_before_any_section_to_root() -> None:
    specs = parse_template("SHODAN_API_KEY=   # Shodan\n## HEXA-SEC\nOTHER_KEY=   # x\n")
    assert specs[0].section == "ROOT"
    assert specs[0].key == "SHODAN_API_KEY"
    assert specs[1].section == "HEXA-SEC"


def test_validate_template_documented_and_empty_values() -> None:
    assert validate_template(parse_template(TEMPLATE)) == []


def test_validate_template_rejects_undocumented_key() -> None:
    specs = parse_template("## HEXA-SEC\nSHODAN_API_KEY=\n")
    violations = validate_template(specs)
    assert any("undocumented key" in v for v in violations)


def test_validate_template_rejects_committed_secret_value() -> None:
    specs = parse_template("## HEXA-SEC\nSHODAN_API_KEY=supersecretvalue\n")
    violations = validate_template(specs)
    assert any("non-empty secret in template" in v for v in violations)


def test_validate_template_rejects_committed_secret_even_when_documented() -> None:
    specs = parse_template("## HEXA-SEC\nSHODAN_API_KEY=supersecretvalue   # Shodan\n")
    violations = validate_template(specs)
    assert any("non-empty secret in template" in v for v in violations)


def test_validate_template_rejects_duplicate_key() -> None:
    specs = parse_template("## HEXA-SEC\nA_KEY=   # a\nA_KEY=   # b\n")
    violations = validate_template(specs)
    assert any("duplicate key" in v for v in violations)


def test_validate_env_rejects_unknown_key() -> None:
    specs = parse_template(TEMPLATE)
    env = parse_env("NOT_A_REAL_KEY=whatever\n")
    violations = validate_env(env, specs)
    assert any("unknown" in v for v in violations)


def test_validate_env_requires_active_section_required_keys() -> None:
    specs = parse_template(TEMPLATE)
    env = parse_env("SHODAN_API_KEY=abc\n")
    violations = validate_env(env, specs)
    assert any("HEXA_SEC_MCP_TOKEN" in v for v in violations)


def test_validate_env_passes_when_required_present() -> None:
    specs = parse_template(TEMPLATE)
    env = parse_env("SHODAN_API_KEY=abc\nHEXA_SEC_MCP_TOKEN=tok\n")
    assert validate_env(env, specs) == []


def test_validate_env_skips_inactive_sections() -> None:
    specs = parse_template(TEMPLATE)
    env = parse_env("SHODAN_API_KEY=abc\nHEXA_SEC_MCP_TOKEN=tok\n")
    violations = validate_env(env, specs)
    assert not any("DATABASE_URL" in v for v in violations)


def test_parse_env_ignores_comments_and_blank() -> None:
    env = parse_env("# a comment\n\nKEY1=value1\n   \nBROKEN LINE\nKEY2=value2 # trailing\n")
    assert env == {"KEY1": "value1", "KEY2": "value2"}


def test_parse_env_comment_starts_at_first_hash_in_value() -> None:
    env = parse_env("TOKEN=abc#def#ghi\n")
    assert env == {"TOKEN": "abc"}


def test_main_valid_template(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / ".env.example").write_text(TEMPLATE, encoding="utf-8")
    assert main(["opencode", str(tmp_path)]) == 0
    assert ".env contract valid." in capsys.readouterr().out


def test_main_missing_template(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["opencode", str(tmp_path)]) == 1
    assert "missing template" in capsys.readouterr().out


def test_main_defaults_to_cwd_without_directory_arg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    assert main(["env_contract"]) == 1


def test_main_env_with_unknown_key(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    (tmp_path / ".env.example").write_text(TEMPLATE, encoding="utf-8")
    (tmp_path / ".env").write_text("UNKNOWN=zzz\n", encoding="utf-8")
    assert main(["opencode", str(tmp_path)]) == 1
    output = capsys.readouterr().out
    assert "unknown key" in output
    assert "violation(s)" in output


def test_main_keeps_template_violations_when_env_is_valid(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / ".env.example").write_text(
        "## HEXA-SEC\nSHODAN_API_KEY=   # Shodan  # REQUIRED\nUNDOC=\n",
        encoding="utf-8",
    )
    (tmp_path / ".env").write_text("SHODAN_API_KEY=abc\n", encoding="utf-8")
    assert main(["opencode", str(tmp_path)]) == 1
    assert "undocumented key" in capsys.readouterr().out


def test_validate_env_required_missing_in_active_section() -> None:
    spec_required = KeySpec("HEXA-SEC", "REQ_KEY", "", "req", True)
    spec_other = KeySpec("HEXA-SEC", "OTHER_KEY", "", "other", False)
    env = parse_env("OTHER_KEY=x\n")
    violations = validate_env(env, [spec_required, spec_other])
    assert violations
    assert any("REQ_KEY" in v for v in violations)
