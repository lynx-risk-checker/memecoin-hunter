from __future__ import annotations
from dataclasses import dataclass
from src.exit import ProtectionState, evaluate_protection

@dataclass(frozen=True)
class PositionObservation:
    token: str
    liquidity_drop_pct: float
    dev_sell_ratio: float
    manipulation_blocked: bool
    exitable: bool
    state: ProtectionState

@dataclass(frozen=True)
class PositionMonitorResult:
    token: str
    emergency: bool
    state: ProtectionState
    reasons: tuple[str,...]

def monitor_position(observation: PositionObservation) -> PositionMonitorResult:
    decision=evaluate_protection(liquidity_drop_pct=observation.liquidity_drop_pct,dev_sell_ratio=observation.dev_sell_ratio,manipulation_blocked=observation.manipulation_blocked,exitability=observation.exitable)
    return PositionMonitorResult(observation.token,decision.emergency,decision.state,decision.reasons)
