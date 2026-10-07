from src.journal import JournalEvent, PaperJournal
from src.paper_journal_metrics import performance_from_journal


def test_journal_trade_events_feed_performance_metrics(tmp_path):
    journal = PaperJournal(tmp_path / "paper.jsonl")
    journal.append(
        JournalEvent(
            "TRADE", 1, "TOKEN_A",
            {"pnl_usd": 2.0, "position_usd": 10.0, "slippage_bps": 5, "latency_ms": 20},
        )
    )
    journal.append(
        JournalEvent(
            "TRADE", 2, "TOKEN_B",
            {"pnl_usd": -1.0, "position_usd": 10.0, "rug_loss": True},
        )
    )
    performance = performance_from_journal(journal.read(), starting_equity_usd=100.0)
    assert performance.trades == 2
    assert performance.pnl_usd == 1.0
    assert performance.rug_losses == 1
    assert performance.max_drawdown_usd == 1.0
