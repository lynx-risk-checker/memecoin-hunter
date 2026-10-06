from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.data.tx_parser import ParsedTransaction


@dataclass(frozen=True)
class WalletTokenStats:
    wallet: str
    mint: str
    buys: int
    sells: int
    bought_ui: float
    sold_ui: float
    net_flow_ui: float


@dataclass(frozen=True)
class WalletIntelligence:
    wallet: str
    transactions: int
    successful_transactions: int
    token_stats: tuple[WalletTokenStats, ...]
    activity_score: float


def build_wallet_intelligence(wallet: str, transactions: Iterable[ParsedTransaction]) -> WalletIntelligence:
    if not wallet.strip():
        raise ValueError("wallet is required")
    txs = tuple(transactions)
    stats: dict[str, list[float | int]] = {}
    successful = sum(1 for tx in txs if tx.success)
    for tx in txs:
        mints = {d.mint for d in tx.token_deltas if d.owner == wallet and d.mint}
        for mint in mints:
            row = stats.setdefault(mint, [0, 0, 0.0, 0.0])
            for d in tx.token_deltas:
                if d.owner != wallet or d.mint != mint:
                    continue
                if d.raw_delta > 0:
                    row[0] += 1; row[2] += d.ui_delta
                elif d.raw_delta < 0:
                    row[1] += 1; row[3] += -d.ui_delta
    token_stats = tuple(
        WalletTokenStats(wallet, mint, int(row[0]), int(row[1]), float(row[2]), float(row[3]), float(row[2]-row[3]))
        for mint, row in sorted(stats.items())
    )
    activity_score = min(1.0, (len(txs)/20.0)*0.5 + (successful/max(len(txs),1))*0.5)
    return WalletIntelligence(wallet, len(txs), successful, token_stats, activity_score)
