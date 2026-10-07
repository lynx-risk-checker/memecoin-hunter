from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from src.narrative import NarrativeSignal

@dataclass(frozen=True)
class NarrativeObservation:
    source: str
    signal: NarrativeSignal
    observed_at: int

class NarrativeSource(Protocol):
    def collect(self) -> tuple[NarrativeObservation, ...]: ...

def merge_narrative_sources(sources: tuple[NarrativeSource, ...]) -> tuple[NarrativeObservation, ...]:
    observations = []
    for source in sources:
        observations.extend(source.collect())
    return tuple(sorted(observations, key=lambda item: item.observed_at))
