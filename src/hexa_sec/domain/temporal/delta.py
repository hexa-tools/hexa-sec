"""ChangeKind + Delta — what changed between two scans (context: temporal, SEC-22).

A ``Delta`` is computed strictly between two distinct snapshots and partitions
the findings into added / resolved / unchanged. Never invents a change: two
scans with identical findings yield an all-UNCHANGED delta.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum

from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.temporal.snapshot import Snapshot


class ChangeKind(Enum):
    """How a finding changed between two scans."""

    ADDED = "added"
    RESOLVED = "resolved"
    UNCHANGED = "unchanged"


@dataclass(frozen=True)
class Delta:
    """The change set between two scan snapshots."""

    before: Snapshot
    after: Snapshot
    added_findings: tuple[FindingId, ...]
    resolved_findings: tuple[FindingId, ...]
    unchanged_count: int

    @property
    def added_count(self) -> int:
        """Number of newly discovered findings."""
        return len(self.added_findings)

    @property
    def resolved_count(self) -> int:
        """Number of findings fixed since the previous scan."""
        return len(self.resolved_findings)

    def changes(self) -> tuple[tuple[FindingId, ChangeKind], ...]:
        """The (finding, kind) pairs, sorted deterministically by finding id."""
        added = sorted(self.added_findings, key=lambda f: f.value)
        resolved = sorted(self.resolved_findings, key=lambda f: f.value)
        return tuple(
            [(finding, ChangeKind.ADDED) for finding in added]
            + [(finding, ChangeKind.RESOLVED) for finding in resolved]
        )

    def __post_init__(self) -> None:
        added = {f.value for f in self.added_findings}
        resolved = {f.value for f in self.resolved_findings}
        if added & resolved:
            raise ValueError("delta is incoherent: a finding cannot be both added and resolved")
        if self.unchanged_count < 0:
            raise ValueError("delta unchanged_count cannot be negative")

    @classmethod
    def compute(
        cls,
        before: Snapshot,
        after: Snapshot,
        before_findings: Iterable[FindingId],
        after_findings: Iterable[FindingId],
    ) -> Delta:
        """Partition the findings into added / resolved / unchanged.

        Raises ``ValueError`` if ``before`` and ``after`` are the same scan — a
        delta is only meaningful between two distinct snapshots.
        """
        if before.scan_id == after.scan_id:
            raise ValueError("delta requires two distinct scans")
        before_idx = {f.value.strip(): f for f in before_findings}
        after_idx = {f.value.strip(): f for f in after_findings}
        added_keys = set(after_idx) - set(before_idx)
        resolved_keys = set(before_idx) - set(after_idx)
        unchanged_count = len(set(before_idx) & set(after_idx))
        return cls(
            before=before,
            after=after,
            added_findings=tuple(FindingId(key) for key in sorted(added_keys)),
            resolved_findings=tuple(FindingId(key) for key in sorted(resolved_keys)),
            unchanged_count=unchanged_count,
        )
