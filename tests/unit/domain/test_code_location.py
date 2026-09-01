"""Tests for the CodeLocation value object (context: code_risk, SEC-14)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.code_risk.code_location import CodeLocation


def test_code_location_creation() -> None:
    location = CodeLocation(file="src/app.py", line=42)
    assert location.file == "src/app.py"
    assert location.line == 42


def test_code_location_trims_file() -> None:
    assert CodeLocation(file="  src/app.py  ", line=1).file == "src/app.py"


def test_code_location_rejects_empty_file() -> None:
    with pytest.raises(ValueError):
        CodeLocation(file="", line=1)


def test_code_location_rejects_blank_file() -> None:
    with pytest.raises(ValueError):
        CodeLocation(file="   ", line=1)


def test_code_location_rejects_zero_line() -> None:
    with pytest.raises(ValueError):
        CodeLocation(file="src/app.py", line=0)


def test_code_location_rejects_negative_line() -> None:
    with pytest.raises(ValueError):
        CodeLocation(file="src/app.py", line=-1)
