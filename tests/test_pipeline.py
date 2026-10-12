import pytest

from src.exit import ProtectionState
from src.pipeline import CandidateContext, evaluate_candidate
from src.strategy.edge import EdgeDecision, EdgeInput


def _safe_context(**overrides) -> CandidateContext:
    values = {
        "token": "TOKEN",
        "edge": EdgeInput(1.0, 2.0, 1.0, 10.0, True, False, 1.0),
        "position_usd": 5.0,
        "slippage_bps": 50,
    }
    values.update(overrides)
    return CandidateContext(**values)


def _evaluate(context: CandidateContext):
    return evaluate_candidate(
        context,
        dry_run=True,
        paper_trading=True,
        daily_loss=0,
        max_daily_loss=10,
        max_position_usd=10,
        max_slippage_bps=100,
    )


@pytest.mark.parametrize(
    ("overrides", "expected_reason"),
    [
        ({"liquidity_drop_pct": 50}, "LIQUIDITY_COLLAPSE"),
        ({"dev_sell_ratio": 0.70}, "DEV_SELL_PRESSURE"),
        (
            {
                "edge": EdgeInput(1.0, 2.0, 1.0, 10.0, True, True, 1.0),
            },
            "MANIPULATION_RISK",
        ),
        ({"exitability": False}, "EXITABILITY_LOST"),
        ({"protection_state": ProtectionState.HALTED}, "MISSION_HALTED"),
    ],
)
def test_every_protection_trigger_vetoes_entry(overrides, expected_reason) -> None:
    result = _evaluate(_safe_context(**overrides))

    assert result.protection.emergency is True
    assert expected_reason in result.protection.reasons
    assert result.decision.decision == EdgeDecision.BUY_BLOCKED
    assert result.decision.risk_allowed is False
    assert expected_reason in result.decision.reasons
    assert "PROTECTION_VETO" in result.decision.reasons
    assert "RISK_APPROVED" not in result.decision.reasons


def test_candidate_pipeline_allows_safe_paper_candidate() -> None:
    result = _evaluate(_safe_context())

    assert result.decision.decision == EdgeDecision.BUY_ALLOWED
    assert result.decision.risk_allowed is True
    assert result.protection.emergency is False
    assert "RISK_APPROVED" in result.decision.reasons


def test_protection_veto_preserves_existing_edge_block_reason() -> None:
    context = _safe_context(
        liquidity_drop_pct=60,
        edge=EdgeInput(0.0, 2.0, 1.0, 10.0, True, False, 1.0),
    )

    result = _evaluate(context)

    assert result.decision.decision == EdgeDecision.BUY_BLOCKED
    assert result.decision.risk_allowed is False
    assert "EV_NON_POSITIVE" in result.decision.reasons
    assert "LIQUIDITY_COLLAPSE" in result.decision.reasons
    assert "PROTECTION_VETO" in result.decision.reasons
