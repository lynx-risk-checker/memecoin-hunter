from datetime import datetime, timedelta, timezone

import pytest

from src.forensics.collector import EarlyFlowMetrics
from src.strategy.early_flow import FlowState, assess_early_flow


def make_metrics(**overrides):
    values = dict(
        token_address="TOKEN",
        interval_seconds=60.0,
        price_change_pct=2.0,
        liquidity_change_pct=1.0,
        volume_change_pct=20.0,
        buy_count_change=120,
        sell_count_change=80,
        buy_sell_ratio=1.5,
        unique_buyer_change=None,
        unique_seller_change=None,
        holder_change=None,
        market_cap_change_pct=2.0,
        volume_rate_per_minute=20.0,
        buy_rate_per_minute=120.0,
        sell_rate_per_minute=80.0,
        volume_acceleration_pct=30.0,
        buy_acceleration_pct=40.0,
        sell_acceleration_pct=5.0,
    )
    values.update(overrides)
    return EarlyFlowMetrics(**values)


def test_accelerating_buy_flow():
    result = assess_early_flow(make_metrics())
    assert result.state == FlowState.ACCELERATING_BUY
    assert result.score == pytest.approx(2.0)
    assert "BUY_FLOW_DOMINANT" in result.reasons
    assert "BUY_FLOW_ACCELERATING" in result.reasons
    assert result.data_complete is False


def test_accelerating_sell_flow():
    result = assess_early_flow(
        make_metrics(
            buy_sell_ratio=0.6,
            buy_acceleration_pct=-10.0,
            sell_acceleration_pct=30.0,
        )
    )
    assert result.state == FlowState.ACCELERATING_SELL
    assert result.score == pytest.approx(-2.5)


def test_weakening_flow():
    result = assess_early_flow(
        make_metrics(
            buy_sell_ratio=1.0,
            buy_acceleration_pct=-40.0,
            sell_acceleration_pct=-30.0,
        )
    )
    assert result.state == FlowState.WEAKENING
    assert result.score == pytest.approx(0.0)


def test_insufficient_data():
    result = assess_early_flow(None)
    assert result.state == FlowState.INSUFFICIENT_DATA
    assert result.score == 0.0
    assert result.data_complete is False
