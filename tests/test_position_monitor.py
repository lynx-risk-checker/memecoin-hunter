from src.exit import ProtectionState
from src.position_monitor import PositionObservation, monitor_position

def test_monitor_blocks_when_exitability_is_lost():
    result = monitor_position(PositionObservation(
        token="TOKEN", liquidity_drop_pct=0, dev_sell_ratio=0,
        manipulation_blocked=False, exitable=False, state=ProtectionState.NORMAL))
    assert result.emergency is True
    assert result.state == ProtectionState.HALTED
    assert "EXITABILITY_LOST" in result.reasons

def test_monitor_allows_normal_position():
    result = monitor_position(PositionObservation(
        token="TOKEN", liquidity_drop_pct=0, dev_sell_ratio=0,
        manipulation_blocked=False, exitable=True, state=ProtectionState.NORMAL))
    assert result.emergency is False
    assert result.state == ProtectionState.NORMAL
