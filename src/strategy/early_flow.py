from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from src.forensics.collector import EarlyFlowMetrics


class FlowState(StrEnum):
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    ACCELERATING_BUY = "ACCELERATING_BUY"
    BALANCED = "BALANCED"
    ACCELERATING_SELL = "ACCELERATING_SELL"
    WEAKENING = "WEAKENING"


@dataclass(frozen=True)
class EarlyFlowAssessment:
    state: FlowState
    score: float
    reasons: tuple[str, ...]
    data_complete: bool


def assess_early_flow(
    metrics: EarlyFlowMetrics | None,
    *,
    min_buy_sell_ratio: float = 1.15,
    min_acceleration_pct: float = 20.0,
) -> EarlyFlowAssessment:
    """Classify short-term flow without turning flow alone into a trade signal.

    Missing wallet/holder fields remain missing; they are never inferred.
    """
    if metrics is None:
        return EarlyFlowAssessment(
            state=FlowState.INSUFFICIENT_DATA,
            score=0.0,
            reasons=("INSUFFICIENT_OBSERVATIONS",),
            data_complete=False,
        )

    if min_buy_sell_ratio <= 0:
        raise ValueError("min_buy_sell_ratio must be positive.")
    if min_acceleration_pct < 0:
        raise ValueError("min_acceleration_pct cannot be negative.")

    reasons: list[str] = []
    score = 0.0

    ratio = metrics.buy_sell_ratio
    buy_acc = metrics.buy_acceleration_pct
    sell_acc = metrics.sell_acceleration_pct

    if ratio is not None:
        if ratio >= min_buy_sell_ratio:
            score += 1.0
            reasons.append("BUY_FLOW_DOMINANT")
        elif ratio <= 1.0 / min_buy_sell_ratio:
            score -= 1.0
            reasons.append("SELL_FLOW_DOMINANT")
        else:
            reasons.append("FLOW_NEAR_BALANCED")
    else:
        reasons.append("BUY_SELL_RATIO_UNAVAILABLE")

    if buy_acc is not None and buy_acc >= min_acceleration_pct:
        score += 1.0
        reasons.append("BUY_FLOW_ACCELERATING")
    elif buy_acc is not None and buy_acc < 0:
        score -= 0.5
        reasons.append("BUY_FLOW_WEAKENING")

    if sell_acc is not None and sell_acc >= min_acceleration_pct:
        score -= 1.0
        reasons.append("SELL_FLOW_ACCELERATING")
    elif sell_acc is not None and sell_acc < 0:
        score += 0.5
        reasons.append("SELL_FLOW_WEAKENING")

    if score >= 1.5:
        state = FlowState.ACCELERATING_BUY
    elif score <= -1.5:
        state = FlowState.ACCELERATING_SELL
    elif buy_acc is not None and sell_acc is not None and buy_acc < 0 and sell_acc < 0:
        state = FlowState.WEAKENING
    else:
        state = FlowState.BALANCED

    return EarlyFlowAssessment(
        state=state,
        score=score,
        reasons=tuple(reasons),
        data_complete=(
            metrics.unique_buyer_change is not None
            and metrics.unique_seller_change is not None
            and metrics.holder_change is not None
        ),
    )
