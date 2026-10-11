from datetime import datetime, timezone

from src.radar.models import TokenCandidate
from src.radar.token_radar import RadarPolicy, candidate_filter_reasons, filter_candidates


def test_radar_filters_old_tokens():
    now = datetime.now(timezone.utc)
    candidates = [
        TokenCandidate("A", now, "test", age_seconds=30),
        TokenCandidate("B", now, "test", age_seconds=301),
    ]
    result = filter_candidates(candidates, RadarPolicy(max_age_seconds=300))
    assert [x.address for x in result] == ["A"]


def test_radar_filters_low_liquidity():
    now = datetime.now(timezone.utc)
    candidates = [
        TokenCandidate("A", now, "test", liquidity_usd=100),
        TokenCandidate("B", now, "test", liquidity_usd=10),
    ]
    result = filter_candidates(candidates, RadarPolicy(min_liquidity_usd=50))
    assert [x.address for x in result] == ["A"]


def test_radar_blocks_unknown_liquidity_by_default():
    now = datetime.now(timezone.utc)
    candidates = [
        TokenCandidate("KNOWN", now, "test", liquidity_usd=100),
        TokenCandidate("UNKNOWN", now, "test", liquidity_usd=None),
    ]
    result = filter_candidates(candidates, RadarPolicy(require_liquidity=True))
    assert [x.address for x in result] == ["KNOWN"]


def test_radar_can_allow_unknown_liquidity_when_explicitly_requested():
    now = datetime.now(timezone.utc)
    candidates = [TokenCandidate("UNKNOWN", now, "test", liquidity_usd=None)]
    result = filter_candidates(candidates, RadarPolicy(require_liquidity=False))
    assert [x.address for x in result] == ["UNKNOWN"]


def test_candidate_filter_reasons_match_active_policy_without_changing_it():
    now = datetime.now(timezone.utc)
    candidate = TokenCandidate(
        "OLD_UNKNOWN", now, "test", age_seconds=301, liquidity_usd=None,
    )
    policy = RadarPolicy(max_age_seconds=300, require_liquidity=True)
    assert candidate_filter_reasons(candidate, policy) == [
        "PAIR_AGE_EXCEEDS_MAX_AGE",
        "LIQUIDITY_UNKNOWN",
    ]
    assert filter_candidates([candidate], policy) == []


def test_candidate_filter_reasons_empty_for_qualifying_candidate():
    now = datetime.now(timezone.utc)
    candidate = TokenCandidate("NEW", now, "test", age_seconds=30, liquidity_usd=100)
    assert candidate_filter_reasons(candidate, RadarPolicy()) == []
