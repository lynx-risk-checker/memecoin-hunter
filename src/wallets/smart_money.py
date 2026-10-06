from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.wallets.intelligence import WalletIntelligence

@dataclass(frozen=True)
class SmartMoneyAssessment:
    wallet: str
    token_count: int
    entry_events: int
    exit_events: int
    profitable_proxy_events: int
    win_rate_proxy: float
    early_entry_quality: float
    reliability_score: float

def assess_smart_money(intelligence: WalletIntelligence, *, early_window_mints: Iterable[str] = ()) -> SmartMoneyAssessment:
    early = set(early_window_mints)
    entries = sum(x.buys for x in intelligence.token_stats)
    exits = sum(x.sells for x in intelligence.token_stats)
    profitable = sum(1 for x in intelligence.token_stats if x.sells > 0 and x.net_flow_ui > 0)
    win_rate = profitable / max(exits, 1)
    eligible = [x for x in intelligence.token_stats if x.buys > 0]
    early_quality = sum(1 for x in eligible if x.mint in early) / max(len(eligible), 1)
    reliability = min(1.0, 0.40*min(win_rate,1.0) + 0.30*early_quality + 0.30*intelligence.activity_score)
    return SmartMoneyAssessment(intelligence.wallet, len(intelligence.token_stats), entries, exits, profitable, min(1.0,win_rate), early_quality, reliability)
