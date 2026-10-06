from src.wallets.intelligence import WalletIntelligence, WalletTokenStats
from src.wallets.smart_money import assess_smart_money

def test_smart_money_assessment_uses_wallet_history() -> None:
    i=WalletIntelligence("W",20,20,(WalletTokenStats("W","EARLY",2,1,20.0,8.0,12.0),WalletTokenStats("W","LATE",1,1,5.0,7.0,-2.0)),1.0)
    r=assess_smart_money(i,early_window_mints={"EARLY"})
    assert r.entry_events == 3 and r.exit_events == 2
    assert r.profitable_proxy_events == 1 and r.win_rate_proxy == 0.5
    assert r.early_entry_quality == 0.5 and 0 < r.reliability_score <= 1

def test_empty_history_is_not_smart_money() -> None:
    r=assess_smart_money(WalletIntelligence("W",0,0,(),0.0))
    assert r.entry_events == 0 and r.exit_events == 0 and r.win_rate_proxy == 0.0 and r.reliability_score == 0.0
