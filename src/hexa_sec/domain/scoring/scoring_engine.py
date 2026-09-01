"""The deterministic scoring engine — « corrige CECI d'abord » (context: scoring).

Combines severity, exploitability, exposure, impact and facility into a single
0..100 score via a weighted average. Missing components are renormalized away
(never invented); no components at all yields ``None`` — "score not computed".
"""

from __future__ import annotations

from hexa_sec.domain.scoring.risk_score import RiskScore
from hexa_sec.domain.scoring.score_components import ScoreComponents

_WEIGHTS = {
    "severity": 0.40,
    "exploitability": 0.20,
    "exposure": 0.15,
    "impact": 0.15,
    "facility": 0.10,
}


def compute_score(components: ScoreComponents) -> RiskScore | None:
    """Return the deterministic 0..100 score, or ``None`` if nothing is known."""
    parts: list[float] = []
    weights: list[float] = []

    if components.severity is not None:
        parts.append(components.severity.rank / 4.0)
        weights.append(_WEIGHTS["severity"])

    for name, value in (
        ("exploitability", components.exploitability),
        ("exposure", components.exposure),
        ("impact", components.impact),
        ("facility", components.facility),
    ):
        if value is not None:
            parts.append(value)
            weights.append(_WEIGHTS[name])

    if not parts:
        return None

    weighted = sum(part * weight for part, weight in zip(parts, weights, strict=False))
    normalized = weighted / sum(weights)
    return RiskScore.from_value(round(normalized * 100.0, 1))
