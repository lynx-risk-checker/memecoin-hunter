from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from src.data.tx_parser import ParsedTransaction


@dataclass(frozen=True)
class SynchronizedActivity:
    wallet_a: str
    wallet_b: str
    matched_events: int
    total_events: int
    synchronization_ratio: float


def _events(items: list[ParsedTransaction]) -> set[tuple[int | None, str]]:
    return {
        (item.block_time, delta.mint)
        for item in items
        if item.success
        for delta in item.token_deltas
        if item.block_time is not None
    }


def detect_synchronized_activity(
    transactions: dict[str, list[ParsedTransaction]],
    *,
    window_seconds: int = 10,
) -> tuple[SynchronizedActivity, ...]:
    if window_seconds <= 0:
        raise ValueError("window_seconds must be positive")
    wallets = sorted(transactions)
    result: list[SynchronizedActivity] = []
    for wallet_a, wallet_b in combinations(wallets, 2):
        a = [(t, mint) for t, mint in _events(transactions[wallet_a])]
        b = [(t, mint) for t, mint in _events(transactions[wallet_b])]
        matched = 0
        for time_a, mint_a in a:
            if any(mint_a == mint_b and time_a is not None and time_b is not None and abs(time_a - time_b) <= window_seconds for time_b, mint_b in b):
                matched += 1
        total = max(len(a), len(b))
        if total:
            result.append(SynchronizedActivity(wallet_a, wallet_b, matched, total, matched / total))
    return tuple(result)
