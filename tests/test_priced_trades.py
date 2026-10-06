from src.wallets.trade_reconstruction import TradeMatch
from src.wallets.priced_trades import price_trade_matches


def test_prices_reconstructed_trade_and_calculates_realized_pnl() -> None:
    match = TradeMatch("MINT", 10.0, 100, 160, 60, 10.0)
    result = price_trade_matches([match], {100: 2.0, 160: 3.0})
    assert result[0].invested_usd == 20.0
    assert result[0].proceeds_usd == 30.0
    assert result[0].realized_pnl_usd == 10.0


def test_missing_price_is_not_invented() -> None:
    match = TradeMatch("MINT", 10.0, 100, 160, 60, 10.0)
    assert price_trade_matches([match], {100: 2.0}) == ()
