from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RiskDecision:
    allowed: bool
    reason: str


def veto(
    *,
    dry_run: bool,
    paper_trading: bool,
    expected_value: float,
    daily_loss: float,
    max_daily_loss: float,
    position_usd: float,
    max_position_usd: float,
    slippage_bps: int,
    max_slippage_bps: int,
) -> RiskDecision:
    if not dry_run and not paper_trading:
        return RiskDecision(False, "LIVE_EXECUTION_NOT_IMPLEMENTED")
    if expected_value <= 0:
        return RiskDecision(False, "EV_NON_POSITIVE")
    if daily_loss >= max_daily_loss:
        return RiskDecision(False, "DAILY_LOSS_LIMIT")
    if position_usd <= 0 or position_usd > max_position_usd:
        return RiskDecision(False, "POSITION_LIMIT")
    if slippage_bps < 0 or slippage_bps > max_slippage_bps:
        return RiskDecision(False, "SLIPPAGE_LIMIT")
    return RiskDecision(True, "RISK_APPROVED")
