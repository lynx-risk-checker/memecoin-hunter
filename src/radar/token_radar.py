from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import TokenCandidate


@dataclass(frozen=True)
class RadarPolicy:
    min_liquidity_usd: float = 0.0
    max_age_seconds: float = 300.0
    require_liquidity: bool = False
    min_volume_5m_usd: float = 0.0
    min_volume_1h_usd: float = 0.0
    min_txns_5m_per_minute: float = 0.0

    def __post_init__(self) -> None:
        if self.min_liquidity_usd < 0:
            raise ValueError("Minimum liquidity cannot be negative.")
        if self.max_age_seconds <= 0:
            raise ValueError("Maximum age must be positive.")
        if self.min_volume_5m_usd < 0 or self.min_volume_1h_usd < 0:
            raise ValueError("Minimum volume cannot be negative.")
        if self.min_txns_5m_per_minute < 0:
            raise ValueError("Minimum transaction rate cannot be negative.")


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
        if policy.min_volume_5m_usd > 0:
            if candidate.volume_5m_usd is None or candidate.volume_5m_usd < policy.min_volume_5m_usd:
                continue
        if policy.min_volume_1h_usd > 0:
            if candidate.volume_1h_usd is None or candidate.volume_1h_usd < policy.min_volume_1h_usd:
                continue
        if policy.min_txns_5m_per_minute > 0:
            if candidate.txn_count_5m is None or (candidate.txn_count_5m / 5.0) < policy.min_txns_5m_per_minute:
                continue
        result.append(candidate)
    return result
