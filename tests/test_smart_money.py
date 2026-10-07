import pytest

from src.wallets.intelligence import WalletIntelligence, WalletTokenStats
from src.wallets.semantic_pnl import RealizedSemanticTrade
from src.wallets.smart_money import assess_smart_money


def test_smart_money_does_not_treat_net_flow_as_win_rate() -> None:
    i = WalletIntelligence(
        "W",
        20,
        20,
        (
            WalletTokenStats("W", "EARLY", 2, 1, 20.0, 8.0, 12.0),
            WalletTokenStats("W", "LATE", 1, 1, 5.0, 7.0, -2.0),
        ),
        1.0,
    )
    r = assess_smart_money(i, early_window_mints={"EARLY"})
    assert r.entry_events == 3 and r.exit_events == 2
    assert r.profitable_proxy_events == 0
    assert r.win_rate_proxy == 0.0
    assert r.closed_trade_events == 0
    assert r.pnl_evidence_available is False
    assert r.early_entry_quality == 0.5
    assert r.reliability_score == pytest.approx(0.75)


def test_semantic_realized_pnl_can_support_win_rate() -> None:
    i = WalletIntelligence(
        "W",
        20,
        20,
        (WalletTokenStats("W", "EARLY", 2, 1, 20.0, 8.0, 12.0),),
        1.0,
    )
    trades = (
        RealizedSemanticTrade("EARLY", 1.0, 100, 200, 100, 1.0, 1.2, 1.0, 1.2, 0.2),
        RealizedSemanticTrade("EARLY", 1.0, 300, 400, 100, 1.0, 0.8, 1.0, 0.8, -0.2),
    )
    r = assess_smart_money(i, early_window_mints={"EARLY"}, realized_trades=trades)
    assert r.profitable_proxy_events == 1
    assert r.win_rate_proxy == pytest.approx(0.5)
    assert r.closed_trade_events == 2
    assert r.pnl_evidence_available is True


def test_empty_history_is_not_smart_money() -> None:
    r = assess_smart_money(WalletIntelligence("W", 0, 0, (), 0.0))
    assert r.entry_events == 0
    assert r.exit_events == 0
    assert r.win_rate_proxy == 0.0
    assert r.closed_trade_events == 0
    assert r.reliability_score == 0.0
