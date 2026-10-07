from src.narrative import NarrativeSignal
from src.narrative_source import NarrativeObservation, merge_narrative_sources

class Source:
    def __init__(self, observations): self.observations = observations
    def collect(self): return self.observations

def test_narrative_sources_merge_without_inventing_data():
    a = NarrativeObservation("x", NarrativeSignal("meme", 1, 1, 1), 20)
    b = NarrativeObservation("y", NarrativeSignal("ai", 1, 1, 1), 10)
    result = merge_narrative_sources((Source((a,)), Source((b,))))
    assert [item.observed_at for item in result] == [10, 20]
