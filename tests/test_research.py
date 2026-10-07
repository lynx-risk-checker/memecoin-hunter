from src.research import ResearchObservation, score_research

def test_research_groups_signal_outcomes():
    result=score_research([ResearchObservation("flow",1),ResearchObservation("flow",-1),ResearchObservation("dev",1)])
    assert result[0].signal=="dev"
    assert result[1].observations==2
    assert result[1].mean_outcome==0
