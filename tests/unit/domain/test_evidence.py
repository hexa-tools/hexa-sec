"""Tests for EvidenceId + Evidence (context: evidence)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.evidence.evidence import Evidence, EvidenceId
from hexa_sec.domain.finding.finding import FindingId


def test_evidence_creation() -> None:
    evidence = Evidence(
        evidence_id=EvidenceId("evd_0001"),
        finding_id=FindingId("fnd_0001"),
        scanner="nuclei",
        detail='{"template":"CVE-2024-0001"}',
    )
    assert evidence.scanner == "nuclei"


def test_evidence_rejects_empty_scanner() -> None:
    with pytest.raises(ValueError):
        Evidence(
            evidence_id=EvidenceId("evd_0002"),
            finding_id=FindingId("fnd_0001"),
            scanner="",
            detail="raw",
        )


def test_evidence_rejects_empty_detail() -> None:
    with pytest.raises(ValueError):
        Evidence(
            evidence_id=EvidenceId("evd_0003"),
            finding_id=FindingId("fnd_0001"),
            scanner="nessus",
            detail="",
        )
