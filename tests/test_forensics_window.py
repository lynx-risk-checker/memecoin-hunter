from datetime import datetime, timedelta, timezone

import pytest

from src.forensics.models import TokenSnapshot
from src.forensics.window import summarize_five_minute


def make_snapshot(seconds, **overrides):
    values = dict(
        token_address="TOKEN",
        observed_at=datetime(2026, 10, 6, tzinfo=timezone.utc)
        + timedelta(seconds=seconds),
        price_usd=1.0,
        liquidity_usd=10_000.0,
        volume_usd=2_000.0,
        buy_count=100,
        sell_count=50,
        unique_buyers=None,
        unique_sellers=None,
        holder_count=None,
        market_cap_usd=100_000.0,
    )
    values.update(overrides)
    return TokenSnapshot(**values)


def test_five_minute_summary_uses_first_and_latest_observation():
    snapshots = [
        make_snapshot(0),
        make_snapshot(
            60,
            price_usd=1.1,
            liquidity_usd=10_500,
            volume_usd=2_500,
            buy_count=130,
            sell_count=60,
        ),
        make_snapshot(
            120,
            price_usd=1.2,
            liquidity_usd=11_000,
            volume_usd=3_500,
            buy_count=190,
            sell_count=75,
        ),
    ]

    result = summarize_five_minute(snapshots)

    assert result is not None
    assert result.observation_count == 3
    assert result.elapsed_seconds == pytest.approx(120.0)
    assert result.price_change_pct == pytest.approx(20.0)
    assert result.liquidity_change_pct == pytest.approx(10.0)
    assert result.volume_change_pct == pytest.approx(75.0)
    assert result.buy_count_change == 90
    assert result.sell_count_change == 25
    assert result.volume_rate_per_minute == pytest.approx(37.5)
    assert result.buy_rate_per_minute == pytest.approx(45.0)
    assert result.sell_rate_per_minute == pytest.approx(12.5)
    assert result.data_complete is False


def test_five_minute_summary_excludes_observations_older_than_window():
    snapshots = [
        make_snapshot(0),
        make_snapshot(100),
        make_snapshot(200),
        make_snapshot(301),
    ]

    result = summarize_five_minute(snapshots)

    assert result is not None
    assert result.observation_count == 3
    assert result.elapsed_seconds == pytest.approx(201.0)


def test_five_minute_summary_reports_wallet_fields_when_available():
    snapshots = [
        make_snapshot(
            0,
            unique_buyers=10,
            unique_sellers=5,
            holder_count=100,
        ),
        make_snapshot(
            60,
            unique_buyers=25,
            unique_sellers=8,
            holder_count=130,
        ),
    ]

    result = summarize_five_minute(snapshots)

    assert result is not None
    assert result.unique_buyer_change == 15
    assert result.unique_seller_change == 3
    assert result.holder_change == 30
    assert result.data_complete is True


def test_five_minute_summary_requires_two_observations():
    assert summarize_five_minute([make_snapshot(0)]) is None


def test_five_minute_summary_rejects_mixed_tokens():
    snapshots = [make_snapshot(0), make_snapshot(60, token_address="OTHER")]

    with pytest.raises(ValueError, match="same token"):
        summarize_five_minute(snapshots)
