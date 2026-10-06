from __future__ import annotations

from dataclasses import dataclass

from src.risk import veto
from src.strategy.edge import EdgeAssessment, EdgeDecision, EdgeInput, assess_edge


@dataclass(frozen=True)
class PipelineDecision:
    edge: EdgeAssessment
    risk_allowed: bool
    decision: EdgeDecision
    reasons: tuple[str, ...]


def assess(
    edge_input: EdgeInput,
    *,
    dry_run: bool,
    paper_trading: bool,
    daily_loss: float,
    max_daily_loss: float,
    position_usd: float,
    max_position_usd: float,
    slippage_bps: int,
    max_slippage_bps: int,
) -> PipelineDecision:
    edge = assess_edge(edge_input)
    if edge.decision == EdgeDecision.BUY_BLOCKED:
        return PipelineDecision(edge, False, EdgeDecision.BUY_BLOCKED, edge.reasons)

    risk = veto(
        dry_run=dry_run,
        paper_trading=paper_trading,
        expected_value=edge_input.expected_value,
        daily_loss=daily_loss,
        max_daily_loss=max_daily_loss,
        position_usd=position_usd,
        max_position_usd=max_position_usd,
        slippage_bps=slippage_bps,
        max_slippage_bps=max_slippage_bps,
    )
    if not risk.allowed:
        return PipelineDecision(edge, False, EdgeDecision.BUY_BLOCKED, edge.reasons + (risk.reason,))

    return PipelineDecision(edge, True, edge.decision, edge.reasons + (risk.reason,))
