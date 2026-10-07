from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ValidationInput:
    trades: int
    out_of_sample: bool
    walk_forward: bool
    persistent_journal: bool
    max_drawdown_pct: float
    profitability_evidence: bool
    live_execution_enabled: bool

@dataclass(frozen=True)
class ValidationResult:
    status: str
    reasons: tuple[str,...]

def validate(input: ValidationInput) -> ValidationResult:
    reasons=[]
    if input.live_execution_enabled:
        reasons.append("LIVE_EXECUTION_MUST_REMAIN_LOCKED")
    if input.trades < 0 or input.max_drawdown_pct < 0: raise ValueError("invalid validation values")
    if input.trades < 100: reasons.append("INSUFFICIENT_TRADE_SAMPLE")
    if not input.out_of_sample: reasons.append("OUT_OF_SAMPLE_MISSING")
    if not input.walk_forward: reasons.append("WALK_FORWARD_MISSING")
    if not input.persistent_journal: reasons.append("PERSISTENT_JOURNAL_MISSING")
    if not input.profitability_evidence: reasons.append("PROFITABILITY_EVIDENCE_MISSING")
    return ValidationResult("READY_FOR_RESEARCH" if not reasons else "INSUFFICIENT_EVIDENCE",tuple(reasons))
