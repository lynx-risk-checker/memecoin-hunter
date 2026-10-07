from src.strategy.edge import EdgeDecision, EdgeInput, assess_edge


def base(**overrides):
    values = dict(
        expected_value=0.2,
        flow_score=2.0,
        wallet_support=0.9,
        dev_risk_score=10.0,
        liquidity_ok=True,
        manipulation_blocked=False,
        narrative_score=0.8,
    )
    values.update(overrides)
    return EdgeInput(**values)


def test_edge_allows_multi_signal_alignment() -> None:
    result = assess_edge(base())
    assert result.decision == EdgeDecision.BUY_ALLOWED
    assert result.score >= 0.70


def test_edge_vetoes_manipulation() -> None:
    result = assess_edge(base(manipulation_blocked=True))
    assert result.decision == EdgeDecision.BUY_BLOCKED


def test_edge_waits_when_flow_is_not_confirmed() -> None:
    result = assess_edge(base(flow_score=0.0, wallet_support=0.2, narrative_score=0.2))
    assert result.decision == EdgeDecision.WAIT


def test_edge_uses_cluster_adjusted_smart_money_support() -> None:
    from src.wallets.smart_money_aggregate import SmartMoneyAggregate

    aggregate = SmartMoneyAggregate(
        wallet_count=3,
        independent_cluster_count=2,
        independence_ratio=2 / 3,
        effective_support=0.6,
        average_reliability=0.9,
        pnl_evidence_wallets=2,
    )
    result = assess_edge(base(wallet_support=1.0, smart_money_aggregate=aggregate))
    assert result.score < assess_edge(base(wallet_support=1.0)).score
    assert "CORRELATED_SMART_MONEY_CLUSTER" in result.reasons
