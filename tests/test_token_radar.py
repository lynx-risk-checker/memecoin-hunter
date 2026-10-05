from datetime import datetime, timezone

from src.radar.models import TokenCandidate
from src.radar.token_radar import RadarPolicy, filter_candidates


def test_radar_filters_old_tokens():
    now = datetime.now(timezone.utc)
    candidates = [TokenCandidate("A", now, "test", age_seconds=30), TokenCandidate("B", now, "test", age_seconds=301)]
    result = filter_candidates(candidates, RadarPolicy(max_age_seconds=300))
    assert [x.address for x in result] == ["A"]


def test_radar_filters_low_liquidity():
    now = datetime.now(timezone.utc)
    candidates = [TokenCandidate("A", now, "test", liquidity_usd=100), TokenCandidate("B", now, "test", liquidity_usd=10)]
    result = filter_candidates(candidates, RadarPolicy(min_liquidity_usd=50))
    assert [x.address for x in result] == ["A"]
