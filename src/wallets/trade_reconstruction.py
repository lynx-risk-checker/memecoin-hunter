from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.data.tx_parser import ParsedTransaction


@dataclass(frozen=True)
class PositionLot:
    mint: str
    quantity_ui: float
    entry_time: int
    exit_time: int | None = None
    exit_quantity_ui: float = 0.0

    @property
    def holding_seconds(self) -> int | None:
        if self.exit_time is None:
            return None
        return max(0, self.exit_time - self.entry_time)


@dataclass(frozen=True)
class TradeMatch:
    mint: str
    quantity_ui: float
    entry_time: int
    exit_time: int
    holding_seconds: int
    realized_token_flow_ui: float


def reconstruct_trades(
    wallet: str,
    transactions: Iterable[ParsedTransaction],
) -> tuple[TradeMatch, ...]:
    if not wallet.strip():
        raise ValueError("wallet is required")

    lots: dict[str, list[PositionLot]] = {}
    matches: list[TradeMatch] = []

    ordered = sorted(
        (tx for tx in transactions if tx.success and tx.block_time is not None),
        key=lambda tx: (tx.block_time, tx.slot),
    )

    for tx in ordered:
        assert tx.block_time is not None
        grouped: dict[str, tuple[float, float]] = {}
        for d in tx.token_deltas:
            if d.owner != wallet:
                continue
            buy, sell = grouped.get(d.mint, (0.0, 0.0))
            if d.raw_delta > 0:
                buy += d.ui_delta
            elif d.raw_delta < 0:
                sell += -d.ui_delta
            grouped[d.mint] = (buy, sell)

        for mint, (buy, sell) in grouped.items():
            if buy > 0:
                lots.setdefault(mint, []).append(
                    PositionLot(mint=mint, quantity_ui=buy, entry_time=tx.block_time)
                )
            remaining = sell
            queue = lots.get(mint, [])
            while remaining > 0 and queue:
                lot = queue[0]
                matched = min(remaining, lot.quantity_ui)
                matches.append(
                    TradeMatch(
                        mint=mint,
                        quantity_ui=matched,
                        entry_time=lot.entry_time,
                        exit_time=tx.block_time,
                        holding_seconds=max(0, tx.block_time - lot.entry_time),
                        realized_token_flow_ui=matched,
                    )
                )
                remaining -= matched
                if matched >= lot.quantity_ui:
                    queue.pop(0)
                else:
                    queue[0] = PositionLot(
                        mint=lot.mint,
                        quantity_ui=lot.quantity_ui - matched,
                        entry_time=lot.entry_time,
                    )

    return tuple(matches)
