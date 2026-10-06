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


def build_wallet_intelligence(
    wallet: str,
    transactions: Iterable[ParsedTransaction],
) -> WalletIntelligence:
    if not wallet.strip():
        raise ValueError("wallet is required")

    txs = tuple(transactions)
    stats: dict[str, list[float | int]] = {}
    successful = 0

    for tx in txs:
        if tx.success:
            successful += 1

        mints: set[str] = set()
        for delta in tx.token_deltas:
            if delta.owner != wallet or not delta.mint:
                continue
            mints.add(delta.mint)

        for mint in mints:
            row = stats.setdefault(mint, [0, 0, 0.0, 0.0])
            deltas = [
                d for d in tx.token_deltas
                if d.owner == wallet and d.mint == mint
            ]
            for delta in deltas:
                if delta.raw_delta > 0:
                    row[0] += 1
                    row[2] += delta.ui_delta
                elif delta.raw_delta < 0:
                    row[1] += 1
                    row[3] += -delta.ui_delta

    token_stats = tuple(
        WalletTokenStats(
            wallet=wallet,
            mint=mint,
            buys=int(row[0]),
            sells=int(row[1]),
            bought_ui=float(row[2]),
            sold_ui=float(row[3]),
            net_flow_ui=float(row[2] - row[3]),
        )
        for mint, row in sorted(stats.items())
    )

    activity_score = min(
        1.0,
        (len(txs) / 20.0) * 0.5
        + (successful / max(len(txs), 1)) * 0.5,
    )

    return WalletIntelligence(
        wallet=wallet,
        transactions=len(txs),
        successful_transactions=successful,
        token_stats=token_stats,
        activity_score=activity_score,
    )
