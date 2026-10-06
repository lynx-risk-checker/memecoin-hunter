from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Decision(StrEnum):
    BUY_ALLOWED = "BUY_ALLOWED"
    WATCH = "WATCH"
    WAIT = "WAIT"
    BUY_BLOCKED = "BUY_BLOCKED"


@dataclass(frozen=True)
class DecisionInput:
    expected_value: float
    flow_score: float
    dev_risk_score: float
    liquidity_ok: bool


@dataclass(frozen=True)
class DecisionResult:
    decision: Decision
    reasons: tuple[str, ...]


def decide(value: DecisionInput) -> DecisionResult:
    reasons: list[str] = []
    if value.expected_value <= 0:
        reasons.append("EV_NON_POSITIVE")
    if not value.liquidity_ok:
        reasons.append("LIQUIDITY_NOT_EXITABLE")
    if value.dev_risk_score >= 70:
        reasons.append("DEV_RISK_HIGH")
    if reasons:
        return DecisionResult(Decision.BUY_BLOCKED, tuple(reasons))
    if value.flow_score >= 1.5:
        return DecisionResult(Decision.BUY_ALLOWED, ("FLOW_SUPPORTS_ENTRY",))
    if value.flow_score > 0:
        return DecisionResult(Decision.WATCH, ("FLOW_POSITIVE_BUT_NOT_STRONG",))
    return DecisionResult(Decision.WAIT, ("FLOW_NOT_CONFIRMED",))
