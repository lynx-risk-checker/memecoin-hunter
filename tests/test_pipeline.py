from src.exit import ProtectionState
from src.pipeline import CandidateContext, evaluate_candidate
from src.strategy.edge import EdgeDecision, EdgeInput


def test_candidate_pipeline_blocks_when_protection_fails() -> None:
    result = evaluate_candidate(
        CandidateContext(
            token="TOKEN",
            edge=EdgeInput(1.0, 2.0, 1.0, 10.0, True, False, 1.0),
            position_usd=5.0,
            slippage_bps=50,
            liquidity_drop_pct=60,
            exitability=True,
        ),
        dry_run=True,
        paper_trading=True,
        daily_loss=0,
        max_daily_loss=10,
        max_position_usd=10,
        max_slippage_bps=100,
    )
    assert result.decision.decision == EdgeDecision.BUY_ALLOWED
    assert result.protection.emergency is True


def test_candidate_pipeline_allows_safe_paper_candidate() -> None:
    result = evaluate_candidate(
        CandidateContext(
            token="TOKEN",
            edge=EdgeInput(1.0, 2.0, 1.0, 10.0, True, False, 1.0),
            position_usd=5.0,
            slippage_bps=50,
        ),
        dry_run=True,
        paper_trading=True,
        daily_loss=0,
        max_daily_loss=10,
        max_position_usd=10,
        max_slippage_bps=100,
    )
    assert result.decision.decision == EdgeDecision.BUY_ALLOWED
    assert result.decision.risk_allowed is True
    assert result.protection.emergency is False
