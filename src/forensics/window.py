from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from .collector import EarlyFlowMetrics
from .engine import compare_snapshots
from .models import TokenSnapshot


@dataclass(frozen=True)
class FiveMinuteForensics:
    """Aggregated forensic state over a trailing five-minute observation window."""

    token_address: str
    observation_count: int
    elapsed_seconds: float
    window_seconds: float
    price_change_pct: float
    liquidity_change_pct: float
    volume_change_pct: float
    buy_count_change: int
    sell_count_change: int
    buy_sell_ratio: float | None
    unique_buyer_change: int | None
    unique_seller_change: int | None
    holder_change: int | None
    market_cap_change_pct: float | None
    volume_rate_per_minute: float
    buy_rate_per_minute: float
    sell_rate_per_minute: float
    volume_acceleration_pct: float | None
    buy_acceleration_pct: float | None
    sell_acceleration_pct: float | None
    data_complete: bool


def _rate_per_minute(value: float, elapsed_seconds: float) -> float:
    if elapsed_seconds <= 0:
        raise ValueError("Elapsed time must be positive.")
    return value * 60.0 / elapsed_seconds


def _optional_change(previous: int | None, current: int | None) -> int | None:
    if previous is None or current is None:
        return None
    return current - previous


def summarize_five_minute(
    snapshots: tuple[TokenSnapshot, ...] | list[TokenSnapshot],
    *,
    max_window_seconds: float = 300.0,
) -> FiveMinuteForensics | None:
    """Summarize real observations without fabricating unavailable fields."""
    if max_window_seconds <= 0:
        raise ValueError("max_window_seconds must be positive.")
    if len(snapshots) < 2:
        return None

    ordered = list(snapshots)
    for left, right in zip(ordered, ordered[1:]):
        if right.observed_at <= left.observed_at:
            raise ValueError("Snapshots must be strictly time ordered.")
        if left.token_address != right.token_address:
            raise ValueError("Snapshots must belong to the same token.")

    latest = ordered[-1]
    cutoff = latest.observed_at - timedelta(seconds=max_window_seconds)
    window = [snapshot for snapshot in ordered if snapshot.observed_at >= cutoff]

    if len(window) < 2:
        return None

    first = window[0]
    elapsed = (latest.observed_at - first.observed_at).total_seconds()
    delta = compare_snapshots(first, latest)

    previous_delta = (
        compare_snapshots(window[-3], window[-2])
        if len(window) >= 3
        else None
    )
    latest_delta = compare_snapshots(window[-2], latest)

    volume_rate = _rate_per_minute(delta.volume_change_pct, elapsed)
    buy_rate = _rate_per_minute(delta.buy_count_change, elapsed)
    sell_rate = _rate_per_minute(delta.sell_count_change, elapsed)

    volume_acceleration = None
    buy_acceleration = None
    sell_acceleration = None
    if previous_delta is not None:
        previous_elapsed = previous_delta.elapsed_seconds
        previous_volume_rate = _rate_per_minute(
            previous_delta.volume_change_pct, previous_elapsed
        )
        previous_buy_rate = _rate_per_minute(
            previous_delta.buy_count_change, previous_elapsed
        )
        previous_sell_rate = _rate_per_minute(
            previous_delta.sell_count_change, previous_elapsed
        )

        def acceleration(previous_rate: float, current_rate: float) -> float:
            if previous_rate == 0:
                return 0.0 if current_rate == 0 else float("inf")
            return ((current_rate - previous_rate) / abs(previous_rate)) * 100.0

        volume_acceleration = acceleration(previous_volume_rate, _rate_per_minute(
            latest_delta.volume_change_pct, latest_delta.elapsed_seconds
        ))
        buy_acceleration = acceleration(previous_buy_rate, _rate_per_minute(
            latest_delta.buy_count_change, latest_delta.elapsed_seconds
        ))
        sell_acceleration = acceleration(previous_sell_rate, _rate_per_minute(
            latest_delta.sell_count_change, latest_delta.elapsed_seconds
        ))

    return FiveMinuteForensics(
        token_address=latest.token_address,
        observation_count=len(window),
        elapsed_seconds=elapsed,
        window_seconds=max_window_seconds,
        price_change_pct=delta.price_change_pct,
        liquidity_change_pct=delta.liquidity_change_pct,
        volume_change_pct=delta.volume_change_pct,
        buy_count_change=delta.buy_count_change,
        sell_count_change=delta.sell_count_change,
        buy_sell_ratio=delta.buy_sell_ratio,
        unique_buyer_change=_optional_change(first.unique_buyers, latest.unique_buyers),
        unique_seller_change=_optional_change(first.unique_sellers, latest.unique_sellers),
        holder_change=_optional_change(first.holder_count, latest.holder_count),
        market_cap_change_pct=delta.market_cap_change_pct,
        volume_rate_per_minute=volume_rate,
        buy_rate_per_minute=buy_rate,
        sell_rate_per_minute=sell_rate,
        volume_acceleration_pct=volume_acceleration,
        buy_acceleration_pct=buy_acceleration,
        sell_acceleration_pct=sell_acceleration,
        data_complete=(
            first.unique_buyers is not None
            and latest.unique_buyers is not None
            and first.unique_sellers is not None
            and latest.unique_sellers is not None
            and first.holder_count is not None
            and latest.holder_count is not None
        ),
    )
