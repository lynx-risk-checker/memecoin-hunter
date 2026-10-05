from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TokenSnapshot:
    token_address: str
    observed_at: datetime
    price_usd: float
    liquidity_usd: float
    volume_usd: float
    buy_count: int
    sell_count: int
    unique_buyers: int
    unique_sellers: int
    holder_count: int
    market_cap_usd: float | None = None

    def __post_init__(self) -> None:
        if not self.token_address.strip():
            raise ValueError("Token address is required.")
        if self.price_usd < 0:
            raise ValueError("Price cannot be negative.")
        for name in (
            "liquidity_usd",
            "volume_usd",
        ):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} cannot be negative.")
        for name in (
            "buy_count",
            "sell_count",
            "unique_buyers",
            "unique_sellers",
            "holder_count",
        ):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} cannot be negative.")
        if self.market_cap_usd is not None and self.market_cap_usd < 0:
            raise ValueError("Market cap cannot be negative.")


@dataclass(frozen=True)
class ForensicDelta:
    elapsed_seconds: float
    price_change_pct: float
    liquidity_change_pct: float
    volume_change_pct: float
    buy_count_change: int
    sell_count_change: int
    unique_buyer_change: int
    unique_seller_change: int
    holder_change: int
    market_cap_change_pct: float | None

    @property
    def buy_sell_ratio(self) -> float | None:
        total = self.sell_count_change
        if total <= 0:
            return None
        return self.buy_count_change / total
