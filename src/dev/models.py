from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DevRisk:
    developer: str
    prior_launches: int
    suspicious_launches: int
    sell_events: int
    score: float

    def __post_init__(self) -> None:
        if not self.developer.strip():
            raise ValueError("developer is required")
        if min(self.prior_launches, self.suspicious_launches, self.sell_events) < 0:
            raise ValueError("event counts cannot be negative")
        if not 0 <= self.score <= 100:
            raise ValueError("score must be between 0 and 100")
