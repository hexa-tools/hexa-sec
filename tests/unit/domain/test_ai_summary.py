"""Tests for AiSummary (context: ai_assist)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.ai_assist.ai_summary import AiSummary


def test_ai_summary_creation() -> None:
    summary = AiSummary(text="Your system is at moderate risk.")
    assert "moderate" in summary.text


def test_ai_summary_rejects_empty_text() -> None:
    with pytest.raises(ValueError):
        AiSummary(text="")
