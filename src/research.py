from __future__ import annotations
from dataclasses import dataclass
from math import sqrt

@dataclass(frozen=True)
class ResearchObservation:
    signal: str
    outcome: float

@dataclass(frozen=True)
class ResearchScore:
    signal: str
    observations: int
    mean_outcome: float
    confidence_proxy: float

def score_research(observations: list[ResearchObservation]) -> tuple[ResearchScore,...]:
    groups: dict[str,list[float]]={}
    for item in observations:
        if not item.signal.strip(): raise ValueError("signal is required")
        groups.setdefault(item.signal,[]).append(float(item.outcome))
    result=[]
    for signal,values in sorted(groups.items()):
        mean=sum(values)/len(values)
        confidence=min(1.0,sqrt(len(values))/10.0)
        result.append(ResearchScore(signal,len(values),mean,confidence))
    return tuple(result)
