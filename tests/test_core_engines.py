import pytest

from src.dev.engine import assess_dev_risk
from src.decision import Decision, DecisionInput, decide
from src.execution import ExecutionEngine, ExecutionLockedError, ExecutionRequest
from src.liquidity.engine import assess_liquidity
from src.paper import PaperTrade, summarize
from src.wallets.graph import build_graph, shared_token_overlap
from src.wallets.models import WalletObservation


def test_wallet_graph_overlap():
    items = [
        WalletObservation("A", "T1", "BUY", 10, 1),
        WalletObservation("A", "T2", "BUY", 10, 2),
        WalletObservation("B", "T1", "BUY", 10, 3),
    ]
    graph = build_graph(items)
    assert shared_token_overlap(graph, "A", "B") == 1


def test_dev_risk_increases_with_suspicious_history():
    low = assess_dev_risk("dev", prior_launches=10, suspicious_launches=0, sell_events=0)
    high = assess_dev_risk("dev", prior_launches=10, suspicious_launches=8, sell_events=5)
    assert high.score > low.score


def test_liquidity_blocks_large_position():
    result = assess_liquidity(liquidity_usd=1000, position_usd=100)
    assert result.exitable is False


def test_decision_risk_vetoes():
    result = decide(DecisionInput(1.0, 2.0, 10.0, False))
    assert result.decision == Decision.BUY_BLOCKED


def test_decision_allows_strong_flow_when_risk_passes():
    result = decide(DecisionInput(1.0, 2.0, 10.0, True))
    assert result.decision == Decision.BUY_ALLOWED


def test_paper_summary():
    trades = [
        PaperTrade("T", 1.0, 2.0, 100.0),
        PaperTrade("T", 2.0, 1.0, 100.0),
    ]
    result = summarize(trades)
    assert result["trades"] == 2
    assert result["pnl_usd"] == pytest.approx(0.0)
    assert result["win_rate"] == pytest.approx(0.5)


def test_live_execution_is_locked():
    with pytest.raises(ExecutionLockedError, match="LIVE_EXECUTION_LOCKED"):
        ExecutionEngine().execute(ExecutionRequest("T", 10, 100))
