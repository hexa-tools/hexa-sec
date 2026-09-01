"""Tests for ChangeKind and Delta (context: temporal, SEC-22)."""

from __future__ import annotations

import pytest

from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.temporal.delta import ChangeKind, Delta
from hexa_sec.domain.temporal.snapshot import Snapshot

BEFORE = Snapshot("scan_0001", "2026-01-01")
AFTER = Snapshot("scan_0002", "2026-02-01")


def _fid(value: str) -> FindingId:
    return FindingId(value)


def test_change_kind_members() -> None:
    assert ChangeKind.ADDED.value == "added"
    assert ChangeKind.RESOLVED.value == "resolved"
    assert ChangeKind.UNCHANGED.value == "unchanged"


def test_change_kind_unique() -> None:
    values = [member.value for member in ChangeKind]
    assert len(values) == len(set(values))


def test_delta_compute_added_resolved_unchanged() -> None:
    before = (_fid("cve-1"), _fid("cve-2"))
    after = (_fid("cve-2"), _fid("cve-3"))
    delta = Delta.compute(BEFORE, AFTER, before, after)
    assert delta.added_findings == (_fid("cve-3"),)
    assert delta.resolved_findings == (_fid("cve-1"),)
    assert delta.unchanged_count == 1


def test_delta_new_finding_added() -> None:
    delta = Delta.compute(BEFORE, AFTER, (), (_fid("cve-1"),))
    assert delta.added_count == 1
    assert delta.resolved_count == 0
    assert {k for k, _ in delta.changes()} == {_fid("cve-1")}


def test_delta_fix_resolved() -> None:
    delta = Delta.compute(BEFORE, AFTER, (_fid("cve-1"),), ())
    assert delta.resolved_count == 1
    assert delta.added_count == 0
    assert {k for k, _ in delta.changes()} == {_fid("cve-1")}


def test_delta_identical_findings_all_unchanged() -> None:
    findings = (_fid("cve-1"), _fid("cve-2"))
    delta = Delta.compute(BEFORE, AFTER, findings, findings)
    assert delta.added_findings == ()
    assert delta.resolved_findings == ()
    assert delta.unchanged_count == 2
    assert delta.changes() == ()


def test_delta_no_false_change_for_padded_finding() -> None:
    delta = Delta.compute(BEFORE, AFTER, (_fid("cve-1"),), (_fid("cve-1  "),))
    assert delta.added_findings == ()
    assert delta.resolved_findings == ()
    assert delta.unchanged_count == 1


def test_delta_no_before_findings_all_added() -> None:
    delta = Delta.compute(BEFORE, AFTER, (), (_fid("cve-1"), _fid("cve-2")))
    assert delta.added_count == 2
    assert delta.unchanged_count == 0


def test_delta_no_after_findings_all_resolved() -> None:
    delta = Delta.compute(BEFORE, AFTER, (_fid("cve-1"), _fid("cve-2")), ())
    assert delta.resolved_count == 2
    assert delta.unchanged_count == 0


def test_delta_requires_two_distinct_scans() -> None:
    with pytest.raises(ValueError):
        Delta.compute(BEFORE, BEFORE, (), ())


def test_delta_rejects_overlapping_categories() -> None:
    with pytest.raises(ValueError):
        Delta(
            before=BEFORE,
            after=AFTER,
            added_findings=(_fid("cve-1"),),
            resolved_findings=(_fid("cve-1"),),
            unchanged_count=0,
        )


def test_delta_rejects_negative_unchanged_count() -> None:
    with pytest.raises(ValueError):
        Delta(
            before=BEFORE,
            after=AFTER,
            added_findings=(),
            resolved_findings=(),
            unchanged_count=-1,
        )


def test_delta_changes_sorted() -> None:
    delta = Delta.compute(
        BEFORE,
        AFTER,
        (_fid("cve-2"), _fid("cve-1")),
        (_fid("cve-1"), _fid("cve-3")),
    )
    assert [k.value for k, _ in delta.changes()] == ["cve-3", "cve-2"]
    assert [kind for _, kind in delta.changes()] == [ChangeKind.ADDED, ChangeKind.RESOLVED]
