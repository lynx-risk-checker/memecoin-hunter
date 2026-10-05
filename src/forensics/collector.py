from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Protocol

from .engine import compare_snapshots
from .models import ForensicDelta, TokenSnapshot


class SnapshotProvider(Protocol):
    def snapshot(self, token_address: str) -> TokenSnapshot:
        ...


@dataclass(frozen=True)
class EarlyFlowMetrics:
    token_address: str
    interval_seconds: float
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


def _rate_per_minute(value: float, elapsed_seconds: float) -> float:
    if elapsed_seconds <= 0:
        raise ValueError("Elapsed time must be positive.")
    return value * 60.0 / elapsed_seconds


def _acceleration_pct(previous_rate: float, current_rate: float) -> float:
    if previous_rate == 0:
        if current_rate == 0:
            return 0.0
        return float("inf")
    return ((current_rate - previous_rate) / abs(previous_rate)) * 100.0


class ForensicsCollector:
    """Collects real snapshots and derives deltas without inventing missing data."""

    def __init__(self, provider: SnapshotProvider) -> None:
        self._provider = provider
        self._history: dict[str, list[TokenSnapshot]] = defaultdict(list)

    def observe(self, token_address: str) -> TokenSnapshot:
        snapshot = self._provider.snapshot(token_address)
        if snapshot.token_address != token_address:
            raise ValueError("Snapshot provider returned a different token.")
        history = self._history[token_address]
        if history and snapshot.observed_at <= history[-1].observed_at:
            raise ValueError("Snapshot provider returned non-increasing observation time.")
        history.append(snapshot)
        return snapshot

    def history(self, token_address: str) -> tuple[TokenSnapshot, ...]:
        return tuple(self._history.get(token_address, ()))

    def latest_delta(self, token_address: str) -> ForensicDelta | None:
        history = self._history.get(token_address, ())
        if len(history) < 2:
            return None
        return compare_snapshots(history[-2], history[-1])

    def early_flow(self, token_address: str) -> EarlyFlowMetrics | None:
        history = self._history.get(token_address, ())
        if len(history) < 2:
            return None

        current = compare_snapshots(history[-2], history[-1])
        previous = (
            compare_snapshots(history[-3], history[-2])
            if len(history) >= 3
            else None
        )

        volume_rate = _rate_per_minute(
            current.volume_change_pct, current.elapsed_seconds
        )
        buy_rate = _rate_per_minute(
            current.buy_count_change, current.elapsed_seconds
        )
        sell_rate = _rate_per_minute(
            current.sell_count_change, current.elapsed_seconds
        )

        previous_volume_rate = (
            _rate_per_minute(previous.volume_change_pct, previous.elapsed_seconds)
            if previous is not None
            else None
        )
        previous_buy_rate = (
            _rate_per_minute(previous.buy_count_change, previous.elapsed_seconds)
            if previous is not None
            else None
        )
        previous_sell_rate = (
            _rate_per_minute(previous.sell_count_change, previous.elapsed_seconds)
            if previous is not None
            else None
        )

        return EarlyFlowMetrics(
            token_address=token_address,
            interval_seconds=current.elapsed_seconds,
            price_change_pct=current.price_change_pct,
            liquidity_change_pct=current.liquidity_change_pct,
            volume_change_pct=current.volume_change_pct,
            buy_count_change=current.buy_count_change,
            sell_count_change=current.sell_count_change,
            buy_sell_ratio=current.buy_sell_ratio,
            unique_buyer_change=current.unique_buyer_change,
            unique_seller_change=current.unique_seller_change,
            holder_change=current.holder_change,
            market_cap_change_pct=current.market_cap_change_pct,
            volume_rate_per_minute=volume_rate,
            buy_rate_per_minute=buy_rate,
            sell_rate_per_minute=sell_rate,
            volume_acceleration_pct=(
                _acceleration_pct(previous_volume_rate, volume_rate)
                if previous_volume_rate is not None
                else None
            ),
            buy_acceleration_pct=(
                _acceleration_pct(previous_buy_rate, buy_rate)
                if previous_buy_rate is not None
                else None
            ),
            sell_acceleration_pct=(
                _acceleration_pct(previous_sell_rate, sell_rate)
                if previous_sell_rate is not None
                else None
            ),
        )
