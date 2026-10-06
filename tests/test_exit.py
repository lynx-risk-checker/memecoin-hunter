from src.exit import ProtectionState, evaluate_protection


def test_exit_signal_on_liquidity_collapse() -> None:
    result = evaluate_protection(
        state=ProtectionState.NORMAL,
        liquidity_drop_pct=50,
        dev_sell_ratio=0,
        manipulation_blocked=False,
        exitability=True,
    )
    assert result.emergency is True
    assert "LIQUIDITY_COLLAPSE" in result.reasons


def test_halted_state_is_an_exit_signal() -> None:
    result = evaluate_protection(
        state=ProtectionState.HALTED,
        liquidity_drop_pct=0,
        dev_sell_ratio=0,
        manipulation_blocked=False,
        exitability=True,
    )
    assert result.emergency is True
