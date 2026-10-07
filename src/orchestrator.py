from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from src.pipeline import CandidateContext, PipelineResult, evaluate_candidate

@dataclass(frozen=True)
class OrchestrationResult:
    token: str
    pipeline: PipelineResult
    journal_event: dict[str, object]

class ProductionOrchestrator:
    """Single coordinator for the existing edge -> risk -> protection path."""
    def __init__(self, *, journal: Callable[[dict[str, object]], None] | None = None) -> None:
        self._journal=journal
    def evaluate(self, context: CandidateContext, *, dry_run: bool, paper_trading: bool, daily_loss: float, max_daily_loss: float, max_position_usd: float, max_slippage_bps: int) -> OrchestrationResult:
        result=evaluate_candidate(context,dry_run=dry_run,paper_trading=paper_trading,daily_loss=daily_loss,max_daily_loss=max_daily_loss,max_position_usd=max_position_usd,max_slippage_bps=max_slippage_bps)
        event={"token":context.token,"decision":result.decision.decision.value,"risk_allowed":result.decision.risk_allowed,"protection_emergency":result.protection.emergency,"reasons":list(result.decision.reasons+result.protection.reasons)}
        if self._journal is not None: self._journal(event)
        return OrchestrationResult(context.token,result,event)
