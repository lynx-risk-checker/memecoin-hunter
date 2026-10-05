from datetime import datetime, timedelta, timezone

import pytest

from src.forensics.collector import ForensicsCollector
from src.forensics.models import TokenSnapshot


class FakeProvider:
    def __init__(self, snapshots):
        self.snapshots = iter(snapshots)

    def snapshot(self, token_address):
        return next(self.snapshots)


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


def test_collector_keeps_real_observations_and_derives_delta():
    provider = FakeProvider(
        [
            make_snapshot(0),
            make_snapshot(
                60,
                price_usd=1.1,
                liquidity_usd=10_500,
                volume_usd=2_500,
                buy_count=130,
                sell_count=60,
            ),
        ]
    )
    collector = ForensicsCollector(provider)
    collector.observe("TOKEN")
    collector.observe("TOKEN")

    history = collector.history("TOKEN")
    assert len(history) == 2
    delta = collector.latest_delta("TOKEN")
    assert delta is not None
    assert delta.buy_count_change == 30
    assert delta.sell_count_change == 10
    assert delta.volume_change_pct == pytest.approx(25.0)


def test_early_flow_is_unknown_until_two_observations_exist():
    collector = ForensicsCollector(FakeProvider([make_snapshot(0)]))
    collector.observe("TOKEN")
    assert collector.early_flow("TOKEN") is None


def test_early_flow_acceleration_uses_prior_interval():
    provider = FakeProvider(
        [
            make_snapshot(0),
            make_snapshot(60, volume_usd=2_500, buy_count=130, sell_count=60),
            make_snapshot(120, volume_usd=3_500, buy_count=190, sell_count=75),
        ]
    )
    collector = ForensicsCollector(provider)
    for _ in range(3):
        collector.observe("TOKEN")

    metrics = collector.early_flow("TOKEN")
    assert metrics is not None
    assert metrics.volume_rate_per_minute == pytest.approx(40.0)
    assert metrics.buy_rate_per_minute == pytest.approx(60.0)
    assert metrics.sell_rate_per_minute == pytest.approx(15.0)
    assert metrics.volume_acceleration_pct == pytest.approx(60.0)
    assert metrics.buy_acceleration_pct == pytest.approx(100.0)
    assert metrics.sell_acceleration_pct == pytest.approx(50.0)


def test_collector_rejects_wrong_token_and_non_increasing_time():
    wrong = make_snapshot(0, token_address="OTHER")
    with pytest.raises(ValueError, match="different token"):
        ForensicsCollector(FakeProvider([wrong])).observe("TOKEN")

    same_time = make_snapshot(0)
    collector = ForensicsCollector(FakeProvider([make_snapshot(0), same_time]))
    collector.observe("TOKEN")
    with pytest.raises(ValueError, match="non-increasing"):
        collector.observe("TOKEN")
