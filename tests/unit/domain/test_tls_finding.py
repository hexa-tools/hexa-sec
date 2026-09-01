"""Tests for TlsFinding (context: tls_risk)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.tls_risk.tls_finding import TlsFinding


def test_tls_finding_creation() -> None:
    finding = TlsFinding(host="app.example", expired=True)
    assert finding.expired is True


def test_tls_finding_rejects_empty_host() -> None:
    with pytest.raises(ValueError):
        TlsFinding(host="", expired=False)
