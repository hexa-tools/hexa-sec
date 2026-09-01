"""Tests for the .env contract validator (SEC-2)."""

from __future__ import annotations

from pathlib import Path

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


def test_validate_template_documented_and_empty_values() -> None:
    assert validate_template(parse_template(TEMPLATE)) == []


def test_validate_template_rejects_undocumented_key() -> None:
    specs = parse_template("## HEXA-SEC\nSHODAN_API_KEY=\n")
    assert validate_template(specs)


def test_validate_template_rejects_committed_secret_value() -> None:
    specs = parse_template("## HEXA-SEC\nSHODAN_API_KEY=supersecretvalue\n")
    assert validate_template(specs)


def test_validate_template_rejects_duplicate_key() -> None:
    specs = parse_template("## HEXA-SEC\nA_KEY=   # a\nA_KEY=   # b\n")
    assert validate_template(specs)


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


def test_main_valid_template(tmp_path: Path) -> None:
    (tmp_path / ".env.example").write_text(TEMPLATE, encoding="utf-8")
    assert main(["opencode", str(tmp_path)]) == 0


def test_main_missing_template(tmp_path: Path) -> None:
    assert main(["opencode", str(tmp_path)]) == 1


def test_main_env_with_unknown_key(tmp_path: Path) -> None:
    (tmp_path / ".env.example").write_text(TEMPLATE, encoding="utf-8")
    (tmp_path / ".env").write_text("UNKNOWN=zzz\n", encoding="utf-8")
    assert main(["opencode", str(tmp_path)]) == 1


def test_validate_env_required_missing_in_active_section() -> None:
    spec_required = KeySpec("HEXA-SEC", "REQ_KEY", "", "req", True)
    spec_other = KeySpec("HEXA-SEC", "OTHER_KEY", "", "other", False)
    env = parse_env("OTHER_KEY=x\n")
    violations = validate_env(env, [spec_required, spec_other])
    assert violations
    assert any("REQ_KEY" in v for v in violations)
