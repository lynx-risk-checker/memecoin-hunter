from __future__ import annotations

from dataclasses import dataclass
from time import time
from typing import Callable, Protocol

from src.decision_snapshot import DecisionSnapshot, snapshot_candidate
from src.exit import ProtectionState
from src.journal import JournalEvent
from src.kill_switch import KillSwitch
from src.pipeline import CandidateContext, PipelineResult, evaluate_candidate
from src.strategy.decision_pipeline import PipelineDecision
from src.strategy.edge import EdgeDecision


class JournalSink(Protocol):
    def append(self, event: JournalEvent) -> None: ...


@dataclass(frozen=True)
class OrchestrationResult:
    token: str
    pipeline: PipelineResult
    snapshot: DecisionSnapshot
    journal_event: dict[str, object]


class ProductionOrchestrator:
    """Coordinator for edge -> risk -> protection -> snapshot.

    The orchestrator remains paper/dry-run safe; live execution is not implemented.
    A persistent kill switch vetoes candidate approval without changing the edge score.
    """

    def __init__(
        self,
        *,
        journal: Callable[[dict[str, object]], None] | JournalSink | None = None,
        kill_switch: KillSwitch | None = None,
    ) -> None:
        self._journal = journal
        self._kill_switch = kill_switch

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

        kill_state = self._kill_switch.state() if self._kill_switch is not None else None
        if kill_state is not None and kill_state.enabled:
            result = PipelineResult(
                token=result.token,
                decision=PipelineDecision(
                    edge=result.decision.edge,
                    risk_allowed=False,
                    decision=EdgeDecision.BUY_BLOCKED,
                    reasons=result.decision.reasons + (
                        "KILL_SWITCH_ENABLED",
                        f"KILL_SWITCH_REASON:{kill_state.reason}",
                    ),
                ),
                protection=result.protection,
            )

        snapshot = DecisionSnapshot(
            token=context.token,
            decision=result.decision.decision.value,
            edge_score=result.decision.edge.score,
            risk_allowed=result.decision.risk_allowed,
            protection_state=context.protection_state,
            reasons=result.decision.reasons + result.protection.reasons,
        )
        event = {
            "token": context.token,
            "decision": snapshot.decision,
            "edge_score": snapshot.edge_score,
            "risk_allowed": snapshot.risk_allowed,
            "protection_state": snapshot.protection_state.value,
            "protection_emergency": result.protection.emergency,
            "reasons": list(snapshot.reasons),
        }
        if self._journal is not None:
            if hasattr(self._journal, "append"):
                self._journal.append(
                    JournalEvent(
                        event_type="DECISION",
                        timestamp=int(time()),
                        token=context.token,
                        payload=event,
                    )
                )
            else:
                self._journal(event)
        return OrchestrationResult(context.token, result, snapshot, event)
