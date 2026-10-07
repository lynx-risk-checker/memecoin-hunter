from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class DeveloperEvidence:
    wallet: str
    prior_launches: int
    profitable_launches: int
    failed_launches: int
    rug_events: int
    dev_sell_ratio: float
    funding_reuse_ratio: float

@dataclass(frozen=True)
class DeveloperDNA:
    wallet: str
    risk_score: float
    classification: str
    reasons: tuple[str, ...]

def assess_developer(e: DeveloperEvidence) -> DeveloperDNA:
    if not e.wallet.strip(): raise ValueError("wallet is required")
    ratios=(e.dev_sell_ratio,e.funding_reuse_ratio)
    if any(not 0 <= x <= 1 for x in ratios): raise ValueError("ratios must be between 0 and 1")
    if min(e.prior_launches,e.profitable_launches,e.failed_launches,e.rug_events)<0: raise ValueError("counts cannot be negative")
    reasons=[]; score=0.0
    if e.rug_events>0: score+=45; reasons.append("PRIOR_RUG_EVIDENCE")
    if e.failed_launches>0: score+=min(20,5*e.failed_launches); reasons.append("FAILED_LAUNCH_HISTORY")
    if e.dev_sell_ratio>=0.70: score+=25; reasons.append("HIGH_DEV_SELL_PRESSURE")
    if e.funding_reuse_ratio>=0.70: score+=10; reasons.append("FUNDING_REUSE")
    score=min(100.0,score)
    classification="HIGH_RISK" if score>=70 else "MEDIUM_RISK" if score>=35 else "LOWER_RISK"
    if e.prior_launches==0: reasons.append("NO_PRIOR_LAUNCH_EVIDENCE")
    return DeveloperDNA(e.wallet,score,classification,tuple(reasons))
