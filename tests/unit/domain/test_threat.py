"""Tests for Threat (context: threat_intel)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.threat_intel.threat import Threat


def test_threat_creation() -> None:
    threat = Threat(actor="APT-41", tactic="initial_access")
    assert threat.actor == "APT-41"


def test_threat_rejects_empty_actor() -> None:
    with pytest.raises(ValueError):
        Threat(actor="", tactic="initial_access")


def test_threat_rejects_empty_tactic() -> None:
    with pytest.raises(ValueError):
        Threat(actor="APT-41", tactic="")
