from src.kill_switch import KillSwitch
from src.orchestrator import ProductionOrchestrator
from src.pipeline import CandidateContext
from src.strategy.edge import EdgeDecision, EdgeInput


def make_context() -> CandidateContext:
    return CandidateContext(
        token="TOKEN",
        edge=EdgeInput(
            expected_value=1.0,
            flow_score=2.0,
            wallet_support=1.0,
            dev_risk_score=0.0,
            liquidity_ok=True,
            manipulation_blocked=False,
            narrative_score=1.0,
        ),
        position_usd=1.0,
        slippage_bps=10,
    )


def test_orchestrator_keeps_paper_path_safe():
    events = []
    orchestrator = ProductionOrchestrator(journal=events.append)
    result = orchestrator.evaluate(
        make_context(),
        dry_run=True,
        paper_trading=True,
        daily_loss=0.0,
        max_daily_loss=10.0,
        max_position_usd=10.0,
        max_slippage_bps=100,
    )
    assert result.pipeline.decision.risk_allowed is True
    assert result.snapshot.risk_allowed is True
    assert events[0]["token"] == "TOKEN"


def test_orchestrator_kill_switch_vetoes_candidate(tmp_path):
    switch = KillSwitch(tmp_path / "kill-switch")
    switch.set("manual emergency stop")
    events = []
    orchestrator = ProductionOrchestrator(journal=events.append, kill_switch=switch)

    result = orchestrator.evaluate(
        make_context(),
        dry_run=True,
        paper_trading=True,
        daily_loss=0.0,
        max_daily_loss=10.0,
        max_position_usd=10.0,
        max_slippage_bps=100,
    )

    assert result.pipeline.decision.decision is EdgeDecision.BUY_BLOCKED
    assert result.pipeline.decision.risk_allowed is False
    assert result.snapshot.risk_allowed is False
    assert "KILL_SWITCH_ENABLED" in result.snapshot.reasons
    assert "KILL_SWITCH_REASON:manual emergency stop" in result.snapshot.reasons
    assert events[0]["risk_allowed"] is False
