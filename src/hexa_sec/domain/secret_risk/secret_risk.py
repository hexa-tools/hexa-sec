"""SecretRisk — the consolidated secret inventory (context: secret_risk, SEC-12).

``for_asset`` turns raw findings into a deduplicated, per-asset inventory. It
keeps findings that are marked ``revoked`` (traced, never silently dropped) and
never raises when nothing is found — an empty inventory is the normal answer.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from hexa_sec.domain.secret_risk.secret_finding import SecretFinding
from hexa_sec.domain.secret_risk.secret_type import SecretType


@dataclass(frozen=True)
class SecretRisk:
    """The inventory of secret findings for a single asset."""

    asset: str
    findings: tuple[SecretFinding, ...]

    @property
    def sensitive_count(self) -> int:
        """Number of findings carrying a real (sensitive) credential."""
        return sum(1 for finding in self.findings if finding.severity.sensitive)

    @property
    def critical_count(self) -> int:
        """Number of findings at CRITICAL severity (must-revoke)."""
        return sum(1 for finding in self.findings if finding.severity.is_critical)

    @classmethod
    def for_asset(cls, asset: str, findings: Iterable[SecretFinding]) -> SecretRisk:
        """Build a consolidated inventory for ``asset``.

        Findings for another asset are ignored; a duplicate (asset, type,
        evidence) keeps the first occurrence. Revoked findings are retained
        (marked, never deleted). Finding construction already enforces that
        evidence is present — no speculation can reach the inventory.
        """
        seen: dict[tuple[str, SecretType, str], SecretFinding] = {}
        for finding in findings:
            if finding.asset != asset:
                continue
            key = (finding.asset, finding.secret_type, finding.evidence)
            existing = seen.get(key)
            if existing is None or (finding.revoked and not existing.revoked):
                seen[key] = finding
        return cls(asset=asset, findings=tuple(seen.values()))
