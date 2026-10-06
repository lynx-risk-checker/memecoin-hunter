from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.wallets.trade_reconstruction import TradeMatch


@dataclass(frozen=True)
class PricedTrade:
    mint: str
    quantity_ui: float
    entry_time: int
    exit_time: int
    holding_seconds: int
    entry_price_usd: float
    exit_price_usd: float

    @property
    def invested_usd(self) -> float:
        return self.quantity_ui * self.entry_price_usd

    @property
    def proceeds_usd(self) -> float:
        return self.quantity_ui * self.exit_price_usd

    @property
    def realized_pnl_usd(self) -> float:
        return self.proceeds_usd - self.invested_usd


def price_trade_matches(
    matches: Iterable[TradeMatch],
    prices: dict[int, float],
) -> tuple[PricedTrade, ...]:
    result: list[PricedTrade] = []
    for match in matches:
        entry = prices.get(match.entry_time)
        exit = prices.get(match.exit_time)
        if entry is None or exit is None:
            continue
        if entry <= 0 or exit <= 0:
            raise ValueError("trade prices must be positive")
        result.append(
            PricedTrade(
                mint=match.mint,
                quantity_ui=match.quantity_ui,
                entry_time=match.entry_time,
                exit_time=match.exit_time,
                holding_seconds=match.holding_seconds,
                entry_price_usd=entry,
                exit_price_usd=exit,
            )
        )
    return tuple(result)
