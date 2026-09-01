"""Notification — the collected alerts (context: notification, SEC-25).

``of`` deduplicates alerts by (subject, alert_type, finding): on a duplicate the
highest severity (then channel) wins — deterministic and independent of arrival
order. Nothing raises when no alert is present.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.notification.alert import Alert


@dataclass(frozen=True)
class Notification:
    """The alerts to deliver after a scan."""

    alerts: tuple[Alert, ...]

    @property
    def critical_count(self) -> int:
        """Number of CRITICAL alerts."""
        return sum(1 for alert in self.alerts if alert.severity is Severity.CRITICAL)

    @classmethod
    def of(cls, alerts: Iterable[Alert]) -> Notification:
        """Build the deduplicated alerts, deterministically ordered."""
        seen: dict[tuple[str, str, str | None], Alert] = {}
        for alert in alerts:
            key = (
                alert.subject,
                alert.alert_type.value,
                alert.finding_id.value.strip() if alert.finding_id is not None else None,
            )
            existing = seen.get(key)
            if existing is None or _prefer(alert, existing):
                seen[key] = alert
        return cls(tuple(sorted(seen.values(), key=lambda a: (a.subject, a.alert_type.value))))


def _prefer(candidate: Alert, current: Alert) -> bool:
    """Whether ``candidate`` should replace ``current`` for the same key.

    Highest severity wins, then the deterministically smaller channel.
    """
    candidate_key = (candidate.severity.rank, candidate.channel.value)
    current_key = (current.severity.rank, current.channel.value)
    return candidate_key > current_key
