from src.wallets.economic_links import WalletLinkEvidence
from src.wallets.smart_money import SmartMoneyAssessment
from src.wallets.smart_money_aggregate import aggregate_smart_money


def assessment(wallet: str, reliability: float) -> SmartMoneyAssessment:
    return SmartMoneyAssessment(
        wallet=wallet,
        token_count=1,
        entry_events=1,
        exit_events=1,
        profitable_proxy_events=1,
        win_rate_proxy=1.0,
        early_entry_quality=1.0,
        reliability_score=reliability,
        closed_trade_events=1,
        pnl_evidence_available=True,
    )


def link(left: str, right: str) -> WalletLinkEvidence:
    return WalletLinkEvidence(
        wallet_a=left,
        wallet_b=right,
        shared_tokens=1,
        shared_transactions=1,
        confidence=0.9,
    )


def test_correlated_wallets_contribute_one_best_signal() -> None:
    result = aggregate_smart_money(
        (assessment("A", 0.9), assessment("B", 0.8), assessment("C", 0.7)),
        (link("A", "B"),),
    )
    assert result.wallet_count == 3
    assert result.independent_cluster_count == 2
    assert result.effective_support == 0.8
    assert result.pnl_evidence_wallets == 2


def test_unlinked_wallets_remain_separate_signals() -> None:
    result = aggregate_smart_money(
        (assessment("A", 0.9), assessment("B", 0.7)),
        (),
    )
    assert result.independent_cluster_count == 2
    assert result.effective_support == 0.8
