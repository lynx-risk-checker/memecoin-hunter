from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EdgeDecision(StrEnum):
    BUY_ALLOWED = "BUY_ALLOWED"
    WATCH = "WATCH"
    WAIT = "WAIT"
    BUY_BLOCKED = "BUY_BLOCKED"


@dataclass(frozen=True)
class EdgeInput:
    expected_value: float
    flow_score: float
    wallet_support: float
    dev_risk_score: float
    liquidity_ok: bool
    manipulation_blocked: bool
    narrative_score: float
    wallet_independence: float = 1.0


@dataclass(frozen=True)
class EdgeAssessment:
    decision: EdgeDecision
    score: float
    reasons: tuple[str, ...]


def assess_edge(value: EdgeInput) -> EdgeAssessment:
    if value.expected_value <= 0:
        return EdgeAssessment(EdgeDecision.BUY_BLOCKED, 0.0, ("EV_NON_POSITIVE",))
    if not 0 <= value.wallet_support <= 1:
        raise ValueError("wallet_support must be between 0 and 1")
    if not 0 <= value.narrative_score <= 1:
        raise ValueError("narrative_score must be between 0 and 1")
    if not 0 <= value.dev_risk_score <= 100:
        raise ValueError("dev_risk_score must be between 0 and 100")
    if not 0 <= value.wallet_independence <= 1:
        raise ValueError("wallet_independence must be between 0 and 1")

    reasons = []
    if not value.liquidity_ok:
        reasons.append("LIQUIDITY_NOT_EXITABLE")
    if value.manipulation_blocked:
        reasons.append("MANIPULATION_RISK")
    if value.dev_risk_score >= 70:
        reasons.append("DEV_RISK_HIGH")
    if reasons:
        return EdgeAssessment(EdgeDecision.BUY_BLOCKED, 0.0, tuple(reasons))

    effective_wallet_support = value.wallet_support * value.wallet_independence
    flow_component = (max(-1.0, min(1.0, value.flow_score / 2.0)) + 1.0) / 2.0
    score = (
        0.35 * flow_component
        + 0.25 * effective_wallet_support
        + 0.20 * (1 - value.dev_risk_score / 100)
        + 0.20 * value.narrative_score
    )

    if value.wallet_independence < 1.0:
        reasons.append("CORRELATED_WALLET_PENALTY")

    if score >= 0.70 and value.flow_score >= 1.5:
        return EdgeAssessment(
            EdgeDecision.BUY_ALLOWED, score, tuple(reasons + ["MULTI_SIGNAL_ALIGNMENT"])
        )
    if score >= 0.50:
        return EdgeAssessment(
            EdgeDecision.WATCH, score, tuple(reasons + ["EDGE_PARTIALLY_CONFIRMED"])
        )
    return EdgeAssessment(
        EdgeDecision.WAIT, score, tuple(reasons + ["EDGE_NOT_CONFIRMED"])
    )
