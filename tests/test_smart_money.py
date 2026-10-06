from src.wallets.intelligence import WalletIntelligence, WalletTokenStats
from src.wallets.smart_money import assess_smart_money


def test_smart_money_assessment_uses_wallet_history() -> None:
    intelligence = WalletIntelligence(
        wallet="W",
        transactions=20,
        successful_transactions=20,
        token_stats=(
            WalletTokenStats("W", "EARLY", 2, 1, 20.0, 8.0, 12.0),
            WalletTokenStats("W", "LATE", 1, 1, 5.0, 7.0, -2.0),
        ),
        activity_score=1.0,
    )
    result = assess_smart_money(intelligence, early_window_mints={"EARLY"})
    assert result.entry_events == 3
    assert result.exit_events == 2
    assert result.profitable_proxy_events == 1
    assert result.win_rate_proxy == 0.5
    assert result.early_entry_quality == 0.5
    assert 0 < result.reliability_score <= 1


def test_empty_history_is_not_smart_money() -> None:
    intelligence = WalletIntelligence(
        wallet="W",
        transactions=0,
        successful_transactions=0,
        token_stats=(),
        activity_score=0.0,
    )
    result = assess_smart_money(intelligence)
    assert result.entry_events == 0
    assert result.exit_events == 0
    assert result.win_rate_proxy == 0.0
    assert result.reliability_score == 0.0
