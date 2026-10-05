from __future__ import annotations

from .models import DevRisk


def assess_dev_risk(
    developer: str,
    *,
    prior_launches: int,
    suspicious_launches: int,
    sell_events: int,
) -> DevRisk:
    if min(prior_launches, suspicious_launches, sell_events) < 0:
        raise ValueError("event counts cannot be negative")
    if prior_launches == 0:
        score = 50.0
    else:
        suspicious_rate = suspicious_launches / prior_launches
        score = min(100.0, 100.0 * (0.75 * suspicious_rate + 0.25 * min(sell_events / prior_launches, 1.0)))
    return DevRisk(developer, prior_launches, suspicious_launches, sell_events, score)
