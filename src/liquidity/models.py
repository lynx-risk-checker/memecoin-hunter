from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LiquidityAssessment:
    liquidity_usd: float
    position_usd: float
    estimated_price_impact_pct: float
    exitable: bool
    reason: str

    def __post_init__(self) -> None:
        if self.liquidity_usd <= 0 or self.position_usd <= 0:
            raise ValueError("liquidity and position must be positive")
        if self.estimated_price_impact_pct < 0:
            raise ValueError("price impact cannot be negative")
