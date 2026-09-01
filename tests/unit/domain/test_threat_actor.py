"""Tests for the ThreatActor value object (context: threat_intel, SEC-20)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.threat_intel.threat_actor import ThreatActor


def test_threat_actor_normalizes_fields() -> None:
    actor = ThreatActor("  APT-41  ", "  Ransomware group  ")
    assert actor.identifier == "APT-41"
    assert actor.description == "Ransomware group"


def test_threat_actor_rejects_empty_identifier() -> None:
    with pytest.raises(ValueError):
        ThreatActor("", "Ransomware group")


def test_threat_actor_rejects_blank_identifier() -> None:
    with pytest.raises(ValueError):
        ThreatActor("   ", "Ransomware group")


def test_threat_actor_rejects_blank_description() -> None:
    with pytest.raises(ValueError):
        ThreatActor("APT-41", "")
    with pytest.raises(ValueError):
        ThreatActor("APT-41", "   ")
