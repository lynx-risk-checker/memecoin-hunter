from __future__ import annotations

from dataclasses import dataclass

from src.exit import ProtectionState
from src.pipeline import CandidateContext, PipelineResult, evaluate_candidate
from src.risk import RiskDecision


@dataclass(frozen=True)
class DecisionSnapshot:
    token: str
    decision: str
    edge_score: float
    risk_allowed: bool
    protection_state: ProtectionState
    reasons: tuple[str, ...]


def snapshot_candidate(
    context: CandidateContext,
    *,
    dry_run: bool = True,
    paper_trading: bool = True,
    daily_loss: float = 0.0,
    max_daily_loss: float = 10.0,
    max_position_usd: float = 10.0,
    max_slippage_bps: int = 100,
) -> DecisionSnapshot:
    result: PipelineResult = evaluate_candidate(
        context,
        dry_run=dry_run,
        paper_trading=paper_trading,
        daily_loss=daily_loss,
        max_daily_loss=max_daily_loss,
        max_position_usd=max_position_usd,
        max_slippage_bps=max_slippage_bps,
    )
    reasons = result.decision.reasons + result.protection.reasons
    return DecisionSnapshot(
        token=context.token,
        decision=result.decision.decision.value,
        edge_score=result.decision.edge.score,
        risk_allowed=result.decision.risk_allowed,
        protection_state=result.protection.state,
        reasons=reasons,
    )
