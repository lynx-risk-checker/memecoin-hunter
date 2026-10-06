from src.paper_metrics import PaperTradeRecord, summarize_performance


def test_performance_metrics_include_drawdown_and_execution_metrics() -> None:
    trades = [
        PaperTradeRecord("A", 100.0, 100.0, slippage_bps=5, latency_ms=100),
        PaperTradeRecord("B", -40.0, 100.0, slippage_bps=10, latency_ms=200, rug_loss=True),
        PaperTradeRecord("C", 60.0, 100.0, slippage_bps=15, latency_ms=300),
    ]

    result = summarize_performance(trades, 1000.0)

    assert result.trades == 3
    assert result.pnl_usd == 120.0
    assert result.win_rate == 2 / 3
    assert result.expectancy_usd == 40.0
    assert result.profit_factor == 4.0
    assert result.max_drawdown_usd == 40.0
    assert result.rug_losses == 1
    assert result.average_slippage_bps == 10.0
    assert result.average_latency_ms == 200.0
