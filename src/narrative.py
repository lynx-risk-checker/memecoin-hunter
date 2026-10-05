from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NarrativeSignal:
    topic: str
    attention_velocity: float
    persistence: float
    onchain_confirmation: float

    def score(self) -> float:
        values = (self.attention_velocity, self.persistence, self.onchain_confirmation)
        if any(v < 0 for v in values):
            raise ValueError("narrative inputs cannot be negative")
        return sum(values) / 3.0


def classify(signal: NarrativeSignal) -> str:
    score = signal.score()
    if score >= 0.75:
        return "STRONG"
    if score >= 0.40:
        return "MODERATE"
    return "WEAK"
