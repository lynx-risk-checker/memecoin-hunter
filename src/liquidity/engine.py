from __future__ import annotations

from .models import LiquidityAssessment


def assess_liquidity(
    *,
    liquidity_usd: float,
    position_usd: float,
    max_price_impact_pct: float = 5.0,
) -> LiquidityAssessment:
    if liquidity_usd <= 0 or position_usd <= 0:
        raise ValueError("liquidity and position must be positive")
    if max_price_impact_pct <= 0:
        raise ValueError("max_price_impact_pct must be positive")
    impact = (position_usd / liquidity_usd) * 100.0
    exitable = impact <= max_price_impact_pct
    return LiquidityAssessment(
        liquidity_usd=liquidity_usd,
        position_usd=position_usd,
        estimated_price_impact_pct=impact,
        exitable=exitable,
        reason="EXITABLE" if exitable else "PRICE_IMPACT_TOO_HIGH",
    )
