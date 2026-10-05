from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import TokenCandidate


@dataclass(frozen=True)
class RadarPolicy:
    min_liquidity_usd: float = 0.0
    max_age_seconds: float = 300.0
    require_liquidity: bool = False

    def __post_init__(self) -> None:
        if self.min_liquidity_usd < 0:
            raise ValueError("Minimum liquidity cannot be negative.")
        if self.max_age_seconds <= 0:
            raise ValueError("Maximum age must be positive.")


def filter_candidates(
    candidates: Iterable[TokenCandidate], policy: RadarPolicy
) -> list[TokenCandidate]:
    result = []
    for candidate in candidates:
        if candidate.age_seconds is not None and candidate.age_seconds > policy.max_age_seconds:
            continue
        if policy.require_liquidity and candidate.liquidity_usd is None:
            continue
        if candidate.liquidity_usd is not None and candidate.liquidity_usd < policy.min_liquidity_usd:
            continue
        result.append(candidate)
    return result
