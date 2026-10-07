from __future__ import annotations

from dataclasses import dataclass
from time import time
from typing import Callable

from src.decision_snapshot import DecisionSnapshot, snapshot_candidate
from src.journal import JournalEvent
from src.pipeline import CandidateContext, PipelineResult, evaluate_candidate


@dataclass(frozen=True)
class OrchestrationResult:
    token: str
    pipeline: PipelineResult
    snapshot: DecisionSnapshot
    journal_event: dict[str, object]


class ProductionOrchestrator:
    """Single coordinator for edge -> risk -> protection -> decision snapshot.

    The orchestrator remains paper/dry-run safe; live execution is not implemented.
    """

    def __init__(
        self,
        *,
        journal: Callable[[dict[str, object]], None] | Callable[[JournalEvent], None] | None = None,
    ) -> None:
        self._journal = journal

    def evaluate(
        self,
        context: CandidateContext,
        *,
        dry_run: bool,
        paper_trading: bool,
        daily_loss: float,
        max_daily_loss: float,
        max_position_usd: float,
        max_slippage_bps: int,
    ) -> OrchestrationResult:
        result = evaluate_candidate(
            context,
            dry_run=dry_run,
            paper_trading=paper_trading,
            daily_loss=daily_loss,
            max_daily_loss=max_daily_loss,
            max_position_usd=max_position_usd,
            max_slippage_bps=max_slippage_bps,
        )
        snapshot = snapshot_candidate(
            context,
            dry_run=dry_run,
            paper_trading=paper_trading,
            daily_loss=daily_loss,
            max_daily_loss=max_daily_loss,
            max_position_usd=max_position_usd,
            max_slippage_bps=max_slippage_bps,
        )
        reasons = result.decision.reasons + result.protection.reasons
        event = {
            "token": context.token,
            "decision": snapshot.decision,
            "edge_score": snapshot.edge_score,
            "risk_allowed": snapshot.risk_allowed,
            "protection_state": snapshot.protection_state.value,
            "protection_emergency": result.protection.emergency,
            "reasons": list(reasons),
        }
        if self._journal is not None:
            if isinstance(self._journal, Callable):
                try:
                    self._journal(event)
                except TypeError:
                    self._journal(
                        JournalEvent(
                            event_type="DECISION",
                            timestamp=int(time()),
                            token=context.token,
                            payload=event,
                        )
                    )
        return OrchestrationResult(context.token, result, snapshot, event)
