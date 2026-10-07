from src.orchestrator import ProductionOrchestrator
from src.pipeline import CandidateContext
from src.strategy.edge import EdgeInput

def test_orchestrator_keeps_paper_path_safe():
    events=[]
    orchestrator=ProductionOrchestrator(journal=events.append)
    context=CandidateContext(token="TOKEN",edge=EdgeInput(expected_value=1.0,flow_score=2.0,wallet_support=1.0,dev_risk_score=0.0,liquidity_ok=True,manipulation_blocked=False,narrative_score=1.0),position_usd=1.0,slippage_bps=10)
    result=orchestrator.evaluate(context,dry_run=True,paper_trading=True,daily_loss=0.0,max_daily_loss=10.0,max_position_usd=10.0,max_slippage_bps=100)
    assert result.pipeline.decision.risk_allowed is True
    assert events[0]["token"]=="TOKEN"
