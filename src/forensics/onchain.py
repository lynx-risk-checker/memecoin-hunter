from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.data.tx_parser import ParsedTransaction


@dataclass(frozen=True)
class OnChainFlow:
    signature: str | None
    block_time: int
    token_mint: str
    buy_volume_ui: float
    sell_volume_ui: float
    buyer_wallets: frozenset[str]
    seller_wallets: frozenset[str]

    @property
    def net_flow_ui(self) -> float:
        return self.buy_volume_ui - self.sell_volume_ui


@dataclass(frozen=True)
class FiveMinuteOnChainSummary:
    window_seconds: int
    transactions: int
    buy_volume_ui: float
    sell_volume_ui: float
    unique_buyers: int
    unique_sellers: int
    net_flow_ui: float


def infer_token_flow(
    transactions: Iterable[ParsedTransaction],
    *,
    token_mint: str,
) -> tuple[OnChainFlow, ...]:
    if not token_mint.strip():
        raise ValueError("token_mint is required")

    flows: list[OnChainFlow] = []
    for tx in transactions:
        if not tx.success or tx.block_time is None:
            continue
        inflows = [d for d in tx.token_deltas if d.mint == token_mint and d.raw_delta > 0 and d.owner]
        outflows = [d for d in tx.token_deltas if d.mint == token_mint and d.raw_delta < 0 and d.owner]
        if not inflows and not outflows:
            continue
        buy = sum(d.ui_delta for d in inflows)
        sell = sum(-d.ui_delta for d in outflows)
        flows.append(
            OnChainFlow(
                signature=tx.signature,
                block_time=tx.block_time,
                token_mint=token_mint,
                buy_volume_ui=buy,
                sell_volume_ui=sell,
                buyer_wallets=frozenset(d.owner for d in inflows),
                seller_wallets=frozenset(d.owner for d in outflows),
            )
        )
    return tuple(flows)


def summarize_five_minutes(
    flows: Iterable[OnChainFlow],
    *,
    end_time: int,
    window_seconds: int = 300,
) -> FiveMinuteOnChainSummary:
    if window_seconds <= 0:
        raise ValueError("window_seconds must be positive")
    selected = [item for item in flows if end_time - window_seconds <= item.block_time <= end_time]
    buyers = set().union(*(item.buyer_wallets for item in selected)) if selected else set()
    sellers = set().union(*(item.seller_wallets for item in selected)) if selected else set()
    buy = sum(item.buy_volume_ui for item in selected)
    sell = sum(item.sell_volume_ui for item in selected)
    return FiveMinuteOnChainSummary(
        window_seconds=window_seconds,
        transactions=len(selected),
        buy_volume_ui=buy,
        sell_volume_ui=sell,
        unique_buyers=len(buyers),
        unique_sellers=len(sellers),
        net_flow_ui=buy - sell,
    )
