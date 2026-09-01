"""Tests for the IaCFileName value object (context: iaac_risk, SEC-17)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.iaac_risk.ia_c_file_name import IaCFileName


def test_ia_c_file_name_creation() -> None:
    name = IaCFileName("infra/main.tf")
    assert name.path == "infra/main.tf"


def test_ia_c_file_name_trims_path() -> None:
    assert IaCFileName("  infra/main.tf  ").path == "infra/main.tf"


def test_ia_c_file_name_rejects_empty() -> None:
    with pytest.raises(ValueError):
        IaCFileName("")


def test_ia_c_file_name_rejects_blank() -> None:
    with pytest.raises(ValueError):
        IaCFileName("   ")
