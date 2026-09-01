"""Temporal — the snapshot history of an asset (context: temporal, SEC-22).

``of`` deduplicates snapshots by (scan_id, taken_on) and ``delta_between``
produces the deterministic :class:`Delta` between two of them.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.finding.finding import FindingId
from hexa_sec.domain.temporal.delta import Delta
from hexa_sec.domain.temporal.snapshot import Snapshot


@dataclass(frozen=True)
class Temporal:
    """The deduplicated scan history of an asset."""

    snapshots: tuple[Snapshot, ...]

    def delta_between(
        self,
        before: Snapshot,
        after: Snapshot,
        before_findings: Iterable[FindingId],
        after_findings: Iterable[FindingId],
    ) -> Delta:
        """Compute the deterministic change set between two snapshots."""
        return Delta.compute(before, after, before_findings, after_findings)

    @classmethod
    def of(cls, snapshots: Iterable[Snapshot]) -> Temporal:
        """Build the history, deduplicated by (scan_id, taken_on) and sorted."""
        seen: dict[tuple[str, str], Snapshot] = {}
        for snapshot in snapshots:
            key = (snapshot.scan_id, snapshot.taken_on)
            if key not in seen:
                seen[key] = snapshot
        return cls(tuple(sorted(seen.values(), key=lambda s: (s.scan_id, s.taken_on))))
