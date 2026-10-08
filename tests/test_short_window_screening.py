from datetime import datetime, timezone

from src.data.dexscreener import DexScreenerClient
from src.radar.models import TokenCandidate
from src.radar.token_radar import RadarPolicy, filter_candidates


def _candidate(**kwargs):
    base = dict(
        address="TOKEN",
        observed_at=datetime.now(timezone.utc),
        source="dexscreener",
        liquidity_usd=10_000.0,
        market_cap_usd=50_000.0,
        age_seconds=60.0,
        volume_5m_usd=25_000.0,
        volume_1h_usd=100_000.0,
        txn_count_5m=100,
        txn_count_1h=900,
    )
    base.update(kwargs)
    return TokenCandidate(**base)


def test_radar_filters_low_short_window_activity():
    policy = RadarPolicy(
        min_volume_5m_usd=20_000.0,
        min_volume_1h_usd=80_000.0,
        min_txns_5m_per_minute=15.0,
    )
    assert filter_candidates([_candidate()], policy)
    assert not filter_candidates([_candidate(volume_5m_usd=19_999.0)], policy)
    assert not filter_candidates([_candidate(txn_count_5m=74)], policy)


def test_enabled_activity_filters_fail_closed_when_data_missing():
    policy = RadarPolicy(min_volume_5m_usd=1.0, min_txns_5m_per_minute=1.0)
    assert filter_candidates([_candidate(volume_5m_usd=None)], policy) == []
    assert filter_candidates([_candidate(txn_count_5m=None)], policy) == []


def test_dexscreener_maps_m5_h1_volume_and_transactions():
    client = DexScreenerClient("https://example.invalid")
    profiles = [{"chainId": "solana", "tokenAddress": "TOKEN1"}]
    pairs = [{
        "chainId": "solana",
        "baseToken": {"address": "TOKEN1", "name": "Example", "symbol": "EX"},
        "pairCreatedAt": 1_700_000_000_000,
        "liquidity": {"usd": 1234.5},
        "marketCap": 9876.5,
        "volume": {"m5": 25000.0, "h1": 100000.0, "h24": 500000.0},
        "txns": {
            "m5": {"buys": 60, "sells": 40},
            "h1": {"buys": 500, "sells": 400},
            "h24": {"buys": 2000, "sells": 1800},
        },
    }]

    client.latest_profiles = lambda: profiles
    client.token_pairs = lambda _: pairs
    result = client.discover()

    assert result[0].volume_5m_usd == 25000.0
    assert result[0].volume_1h_usd == 100000.0
    assert result[0].txn_count_5m == 100
    assert result[0].txn_count_1h == 900
