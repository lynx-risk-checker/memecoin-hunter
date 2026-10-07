from src.decision_snapshot import snapshot_candidate
from src.exit import ProtectionState
from src.pipeline import CandidateContext
from src.strategy.edge import EdgeInput


def test_snapshot_preserves_edge_risk_and_protection():
    context = CandidateContext(
        token="TOKEN",
        edge=EdgeInput(1.0, 2.0, 1.0, 10.0, True, False, 1.0),
        position_usd=1.0,
        slippage_bps=10,
        protection_state=ProtectionState.NORMAL,
    )
    result = snapshot_candidate(context)
    assert result.token == "TOKEN"
    assert result.decision == "BUY_ALLOWED"
    assert result.risk_allowed is True
    assert result.protection_state == ProtectionState.NORMAL
