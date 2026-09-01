"""WebFinding — a normalized OWASP-class web issue (context: web_risk, SEC-10).

An adapter (burp/zap/nuclei) translates a scanner finding into a WebFinding:
the asset, the method (SQLi / XSS / auth / headers...), its OWASP category,
its severity and the raw evidence (no finding without proof).
"""

from __future__ import annotations

from dataclasses import dataclass

from hexa_sec.domain.finding.severity import Severity
from hexa_sec.domain.web_risk.owasp_category import OwaspCategory


@dataclass(frozen=True)
class WebFinding:
    """A normalized web application finding."""

    asset: str
    method: str
    category: OwaspCategory
    severity: Severity = Severity.MEDIUM
    evidence: str = ""

    def __post_init__(self) -> None:
        if not self.asset or not self.asset.strip():
            raise ValueError("web finding asset cannot be empty")
        if not self.method or not self.method.strip():
            raise ValueError("web finding method cannot be empty")
        if not self.evidence or not self.evidence.strip():
            raise ValueError("web finding requires evidence (proof)")
