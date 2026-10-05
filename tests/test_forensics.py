from datetime import datetime, timedelta, timezone

import pytest

from src.forensics.engine import compare_series, compare_snapshots
from src.forensics.models import TokenSnapshot


def snapshot(at_seconds: int, **overrides) -> TokenSnapshot:
    values = dict(
        token_address="TOKEN",
        observed_at=datetime(2026, 10, 6, tzinfo=timezone.utc)
        + timedelta(seconds=at_seconds),
        price_usd=1.0,
        liquidity_usd=10_000.0,
        volume_usd=2_000.0,
        buy_count=100,
        sell_count=50,
        unique_buyers=80,
        unique_sellers=40,
        holder_count=200,
        market_cap_usd=100_000.0,
    )
    values.update(overrides)
    return TokenSnapshot(**values)


def test_snapshot_delta_tracks_flow_and_liquidity():
    delta = compare_snapshots(
        snapshot(0),
        snapshot(
            60,
            price_usd=1.2,
            liquidity_usd=11_000,
            volume_usd=3_000,
            buy_count=140,
            sell_count=65,
            unique_buyers=105,
            unique_sellers=48,
            holder_count=230,
            market_cap_usd=120_000,
        ),
    )

    assert delta.elapsed_seconds == 60
    assert delta.price_change_pct == pytest.approx(20.0)
    assert delta.liquidity_change_pct == pytest.approx(10.0)
    assert delta.volume_change_pct == pytest.approx(50.0)
    assert delta.buy_count_change == 40
    assert delta.sell_count_change == 15
    assert delta.unique_buyer_change == 25
    assert delta.unique_seller_change == 8
    assert delta.holder_change == 30
    assert delta.market_cap_change_pct == pytest.approx(20.0)


def test_series_requires_strict_time_order():
    with pytest.raises(ValueError, match="strictly time ordered"):
        compare_series([snapshot(60), snapshot(60)])


def test_different_tokens_are_rejected():
    with pytest.raises(ValueError, match="same token"):
        compare_snapshots(snapshot(0), snapshot(60, token_address="OTHER"))
