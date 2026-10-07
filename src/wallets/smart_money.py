from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.wallets.intelligence import WalletIntelligence
from src.wallets.semantic_pnl import RealizedSemanticTrade


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
    closed_trade_events: int
    pnl_evidence_available: bool


def assess_smart_money(
    intelligence: WalletIntelligence,
    *,
    early_window_mints: Iterable[str] = (),
    realized_trades: Iterable[RealizedSemanticTrade] = (),
) -> SmartMoneyAssessment:
    """Assess wallet quality without promoting balance-flow netting to PnL.

    Historical win-rate evidence is only calculated from explicitly reconstructed
    semantic DEX trades. Raw wallet token net-flow can describe activity, but it
    cannot prove that a wallet won a trade, so it is never used as a win-rate
    proxy or reliability component.
    """
    early = set(early_window_mints)
    entries = sum(x.buys for x in intelligence.token_stats)
    exits = sum(x.sells for x in intelligence.token_stats)

    trades = tuple(realized_trades)
    profitable = sum(1 for trade in trades if trade.realized_pnl_quote > 0)
    closed = len(trades)
    win_rate = profitable / closed if closed else 0.0
    pnl_evidence_available = closed > 0

    eligible = [x for x in intelligence.token_stats if x.buys > 0]
    early_quality = sum(1 for x in eligible if x.mint in early) / max(len(eligible), 1)

    # Without semantic realized-PnL evidence, reliability is based only on
    # observable activity/early-entry behavior. It must not silently inherit
    # an invented historical performance signal.
    reliability = min(
        1.0,
        0.40 * win_rate
        + 0.30 * early_quality
        + 0.30 * intelligence.activity_score,
    ) if pnl_evidence_available else min(
        1.0,
        0.50 * early_quality
        + 0.50 * intelligence.activity_score,
    )

    return SmartMoneyAssessment(
        intelligence.wallet,
        len(intelligence.token_stats),
        entries,
        exits,
        profitable,
        min(1.0, win_rate),
        early_quality,
        reliability,
        closed,
        pnl_evidence_available,
    )
