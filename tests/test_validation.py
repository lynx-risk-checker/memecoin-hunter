from src.validation import ValidationInput, validate

def test_validation_stays_locked_without_evidence():
    result=validate(ValidationInput(10,False,False,True,20,False,False))
    assert result.status=="INSUFFICIENT_EVIDENCE"
    assert "OUT_OF_SAMPLE_MISSING" in result.reasons

def test_live_execution_can_never_validate():
    result=validate(ValidationInput(1000,True,True,True,5,True,True))
    assert result.status=="INSUFFICIENT_EVIDENCE"
    assert "LIVE_EXECUTION_MUST_REMAIN_LOCKED" in result.reasons
