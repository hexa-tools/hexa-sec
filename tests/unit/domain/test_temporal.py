"""Tests for the Temporal aggregate (context: temporal, SEC-22)."""

from __future__ import annotations

from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.temporal.snapshot import Snapshot
from hexa_sec.domain.temporal.temporal import Temporal


def _fid(value: str) -> FindingId:
    return FindingId(value)


def test_of_deduplicates_snapshots() -> None:
    jan = Snapshot("scan_0001", "2026-01-01")
    feb = Snapshot("scan_0002", "2026-02-01")
    temporal = Temporal.of((jan, jan, feb))
    assert temporal.snapshots == (jan, feb)


def test_of_sorted_by_scan_id() -> None:
    jan = Snapshot("scan_0001", "2026-01-01")
    feb = Snapshot("scan_0002", "2026-02-01")
    temporal = Temporal.of((feb, jan))
    assert temporal.snapshots == (jan, feb)


def test_delta_between() -> None:
    jan = Snapshot("scan_0001", "2026-01-01")
    feb = Snapshot("scan_0002", "2026-02-01")
    temporal = Temporal.of((jan, feb))
    delta = temporal.delta_between(jan, feb, (_fid("cve-1"),), (_fid("cve-2"),))
    assert delta.added_findings == (_fid("cve-2"),)
    assert delta.resolved_findings == (_fid("cve-1"),)


def test_of_empty_is_empty() -> None:
    temporal = Temporal.of(())
    assert temporal.snapshots == ()


def test_is_deterministic() -> None:
    jan = Snapshot("scan_0001", "2026-01-01")
    feb = Snapshot("scan_0002", "2026-02-01")
    first = Temporal.of((jan, feb))
    second = Temporal.of((jan, feb))
    assert first == second
