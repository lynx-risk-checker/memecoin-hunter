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
