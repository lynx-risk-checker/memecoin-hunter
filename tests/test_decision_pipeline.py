from src.strategy.edge import EdgeDecision, EdgeInput
from src.strategy.decision_pipeline import assess


def test_canonical_decision_pipeline_applies_edge_then_risk_veto() -> None:
    result = assess(
        EdgeInput(
            expected_value=1.0,
            flow_score=2.0,
            wallet_support=1.0,
            dev_risk_score=10.0,
            liquidity_ok=True,
            manipulation_blocked=False,
            narrative_score=1.0,
        ),
        dry_run=True,
        paper_trading=True,
        daily_loss=0.0,
        max_daily_loss=10.0,
        position_usd=5.0,
        max_position_usd=10.0,
        slippage_bps=50,
        max_slippage_bps=100,
    )

    assert result.decision == EdgeDecision.BUY_ALLOWED
    assert result.risk_allowed is True


def test_canonical_decision_pipeline_blocks_on_risk() -> None:
    result = assess(
        EdgeInput(
            expected_value=1.0,
            flow_score=2.0,
            wallet_support=1.0,
            dev_risk_score=10.0,
            liquidity_ok=True,
            manipulation_blocked=False,
            narrative_score=1.0,
        ),
        dry_run=True,
        paper_trading=True,
        daily_loss=10.0,
        max_daily_loss=10.0,
        position_usd=5.0,
        max_position_usd=10.0,
        slippage_bps=50,
        max_slippage_bps=100,
    )

    assert result.decision == EdgeDecision.BUY_BLOCKED
    assert "DAILY_LOSS_LIMIT" in result.reasons
