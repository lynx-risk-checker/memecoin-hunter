from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.wallets.intelligence import WalletIntelligence


@dataclass(frozen=True)
class TokenTradeQuality:
    mint: str
    entry_events: int
    exit_events: int
    holding_proxy_events: int
    net_flow_ui: float
    realized_proxy_ui: float


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


def assess_smart_money(
    intelligence: WalletIntelligence,
    *,
    early_window_mints: Iterable[str] = (),
) -> SmartMoneyAssessment:
    early = set(early_window_mints)
    entries = sum(item.buys for item in intelligence.token_stats)
    exits = sum(item.sells for item in intelligence.token_stats)
    profitable = sum(
        1
        for item in intelligence.token_stats
        if item.sells > 0 and item.net_flow_ui > 0
    )
    win_rate = profitable / max(exits, 1)

    eligible = [item for item in intelligence.token_stats if item.buys > 0]
    early_hits = sum(1 for item in eligible if item.mint in early)
    early_quality = early_hits / max(len(eligible), 1)

    activity = intelligence.activity_score
    reliability = min(
        1.0,
        0.40 * min(win_rate, 1.0)
        + 0.30 * early_quality
        + 0.30 * activity,
    )

    return SmartMoneyAssessment(
        wallet=intelligence.wallet,
        token_count=len(intelligence.token_stats),
        entry_events=entries,
        exit_events=exits,
        profitable_proxy_events=profitable,
        win_rate_proxy=min(1.0, win_rate),
        early_entry_quality=early_quality,
        reliability_score=reliability,
    )
