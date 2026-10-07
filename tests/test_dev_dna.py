from src.dev_dna import DeveloperEvidence, assess_developer

def test_rug_history_drives_high_risk():
    result=assess_developer(DeveloperEvidence("DEV",3,0,1,1,0.8,0.8))
    assert result.classification=="HIGH_RISK"
    assert "PRIOR_RUG_EVIDENCE" in result.reasons

def test_no_history_is_explicit():
    result=assess_developer(DeveloperEvidence("DEV",0,0,0,0,0,0))
    assert "NO_PRIOR_LAUNCH_EVIDENCE" in result.reasons
