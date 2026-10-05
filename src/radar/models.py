from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TokenCandidate:
    address: str
    observed_at: datetime
    source: str
    symbol: str | None = None
    name: str | None = None
    liquidity_usd: float | None = None
    market_cap_usd: float | None = None
    age_seconds: float | None = None

    def __post_init__(self) -> None:
        if not self.address.strip():
            raise ValueError("Token address is required.")
        if not self.source.strip():
            raise ValueError("Token source is required.")
        if self.liquidity_usd is not None and self.liquidity_usd < 0:
            raise ValueError("Liquidity cannot be negative.")
        if self.market_cap_usd is not None and self.market_cap_usd < 0:
            raise ValueError("Market cap cannot be negative.")
        if self.age_seconds is not None and self.age_seconds < 0:
            raise ValueError("Age cannot be negative.")
