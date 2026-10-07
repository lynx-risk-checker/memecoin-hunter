import pytest
from src.liquidity.quotes import RouteQuote, assess_route_quote

def test_route_quote_respects_impact_and_slippage():
    assert assess_route_quote(RouteQuote(10,9.8,1.5,40,"route-a")) is True
    assert assess_route_quote(RouteQuote(10,9.8,6.0,40,"route-a")) is False

def test_route_quote_rejects_invalid_amounts():
    with pytest.raises(ValueError):
        assess_route_quote(RouteQuote(0,1,1,1,"route-a"))
