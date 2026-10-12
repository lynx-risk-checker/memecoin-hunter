from __future__ import annotations

from dataclasses import dataclass

from src.exit import ExitSignal, ProtectionState, evaluate_protection
from src.strategy.decision_pipeline import PipelineDecision, assess
from src.strategy.edge import EdgeDecision, EdgeInput


@dataclass(frozen=True)
class CandidateContext:
    token: str
    edge: EdgeInput
    position_usd: float
    slippage_bps: int
    liquidity_drop_pct: float = 0.0
    dev_sell_ratio: float = 0.0
    exitability: bool = True
    protection_state: ProtectionState = ProtectionState.NORMAL


@dataclass(frozen=True)
class PipelineResult:
    token: str
    decision: PipelineDecision
    protection: ExitSignal


def evaluate_candidate(
    context: CandidateContext,
    *,
    dry_run: bool,
    paper_trading: bool,
    daily_loss: float,
    max_daily_loss: float,
    max_position_usd: float,
    max_slippage_bps: int,
) -> PipelineResult:
    decision = assess(
        context.edge,
        dry_run=dry_run,
        paper_trading=paper_trading,
        daily_loss=daily_loss,
        max_daily_loss=max_daily_loss,
        position_usd=context.position_usd,
        max_position_usd=max_position_usd,
        slippage_bps=context.slippage_bps,
        max_slippage_bps=max_slippage_bps,
    )
    protection = evaluate_protection(
        state=context.protection_state,
        liquidity_drop_pct=context.liquidity_drop_pct,
        dev_sell_ratio=context.dev_sell_ratio,
        manipulation_blocked=context.edge.manipulation_blocked,
        exitability=context.exitability,
    )

    # Protection is a final veto for a new entry. A favorable Edge/Risk
    # result must never override an emergency protection condition.
    if protection.emergency:
        prior_reasons = tuple(
            reason for reason in decision.reasons if reason != "RISK_APPROVED"
        )
        decision = PipelineDecision(
            edge=decision.edge,
            risk_allowed=False,
            decision=EdgeDecision.BUY_BLOCKED,
            reasons=prior_reasons + protection.reasons + ("PROTECTION_VETO",),
        )

    return PipelineResult(context.token, decision, protection)
