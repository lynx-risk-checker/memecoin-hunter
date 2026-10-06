from __future__ import annotations

from collections.abc import Sequence

from .models import ForensicDelta, TokenSnapshot


def _pct_change(previous: float, current: float) -> float:
    if previous == 0:
        if current == 0:
            return 0.0
        return float("inf")
    return ((current - previous) / previous) * 100.0


def _optional_change(previous: int | None, current: int | None) -> int | None:
    if previous is None or current is None:
        return None
    return current - previous


def compare_snapshots(previous: TokenSnapshot, current: TokenSnapshot) -> ForensicDelta:
    if previous.token_address != current.token_address:
        raise ValueError("Snapshots must belong to the same token.")

    elapsed = (current.observed_at - previous.observed_at).total_seconds()
    if elapsed <= 0:
        raise ValueError("Current snapshot must be later than previous snapshot.")

    market_cap_change = None
    if previous.market_cap_usd is not None and current.market_cap_usd is not None:
        market_cap_change = _pct_change(previous.market_cap_usd, current.market_cap_usd)

    return ForensicDelta(
        elapsed_seconds=elapsed,
        price_change_pct=_pct_change(previous.price_usd, current.price_usd),
        liquidity_change_pct=_pct_change(previous.liquidity_usd, current.liquidity_usd),
        volume_change_pct=_pct_change(previous.volume_usd, current.volume_usd),
        buy_count_change=current.buy_count - previous.buy_count,
        sell_count_change=current.sell_count - previous.sell_count,
        unique_buyer_change=_optional_change(previous.unique_buyers, current.unique_buyers),
        unique_seller_change=_optional_change(previous.unique_sellers, current.unique_sellers),
        holder_change=_optional_change(previous.holder_count, current.holder_count),
        market_cap_change_pct=market_cap_change,
    )


def compare_series(snapshots: Sequence[TokenSnapshot]) -> list[ForensicDelta]:
    if len(snapshots) < 2:
        return []

    ordered = list(snapshots)
    for left, right in zip(ordered, ordered[1:]):
        if right.observed_at <= left.observed_at:
            raise ValueError("Snapshots must be strictly time ordered.")

    return [
        compare_snapshots(previous, current)
        for previous, current in zip(ordered, ordered[1:])
    ]
