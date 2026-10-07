from src.wallets.economic_links import WalletLinkEvidence
from src.wallets.independence import assess_wallet_independence


def link(left: str, right: str) -> WalletLinkEvidence:
    return WalletLinkEvidence(
        wallet_a=left,
        wallet_b=right,
        shared_tokens=1,
        shared_transactions=0,
        confidence=0.8,
    )


def test_unlinked_wallets_remain_independent() -> None:
    result = assess_wallet_independence(["A", "B", "C"], ())
    assert result.cluster_count == 3
    assert result.independence_ratio == 1.0
    assert result.effective_wallet_count == 3.0


def test_connected_wallets_count_as_one_economic_group() -> None:
    result = assess_wallet_independence(["A", "B", "C"], (link("A", "B"), link("B", "C")))
    assert result.cluster_count == 1
    assert result.independence_ratio == 1 / 3
    assert result.effective_wallet_count == 1.0


def test_edge_penalizes_correlated_wallet_support() -> None:
    from src.strategy.edge import EdgeInput, assess_edge

    base = dict(
        expected_value=0.2,
        flow_score=2.0,
        wallet_support=1.0,
        dev_risk_score=10.0,
        liquidity_ok=True,
        manipulation_blocked=False,
        narrative_score=0.8,
    )
    independent = assess_edge(EdgeInput(**base, wallet_independence=1.0))
    correlated = assess_edge(EdgeInput(**base, wallet_independence=0.25))

    assert correlated.score < independent.score
    assert "CORRELATED_WALLET_PENALTY" in correlated.reasons
