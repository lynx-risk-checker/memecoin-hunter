from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class RouteQuote:
    input_amount: float
    output_amount: float
    price_impact_pct: float
    slippage_bps: int
    route: str

class QuoteProvider(Protocol):
    def quote(self, *, input_mint: str, output_mint: str, amount: float) -> RouteQuote: ...

def assess_route_quote(quote: RouteQuote, *, max_price_impact_pct: float = 5.0, max_slippage_bps: int = 100) -> bool:
    if quote.input_amount <= 0 or quote.output_amount <= 0:
        raise ValueError("quote amounts must be positive")
    if quote.price_impact_pct < 0 or quote.slippage_bps < 0:
        raise ValueError("quote risk metrics cannot be negative")
    return quote.price_impact_pct <= max_price_impact_pct and quote.slippage_bps <= max_slippage_bps
