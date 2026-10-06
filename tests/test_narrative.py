import pytest

from src.narrative import NarrativeSignal, classify
from src.mission import Mission


def test_narrative_classification():
    assert classify(NarrativeSignal("x", 0.9, 0.8, 0.7)) == "STRONG"
    assert classify(NarrativeSignal("x", 0.5, 0.4, 0.3)) == "MODERATE"
    assert classify(NarrativeSignal("x", 0.2, 0.1, 0.0)) == "WEAK"


def test_narrative_rejects_negative_input():
    with pytest.raises(ValueError):
        NarrativeSignal("x", -1, 0, 0).score()


def test_mission_progress():
    mission = Mission()
    assert mission.progress(100_000) == pytest.approx(0.0)
    assert mission.progress(800_000) == pytest.approx(0.5)
    assert mission.progress(1_500_000) == pytest.approx(1.0)
