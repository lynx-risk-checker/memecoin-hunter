from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.wallets.dex_swap_semantics import DexSwapSemanticEvidence


@dataclass(frozen=True)
class RealizedSemanticTrade:
    mint: str
    quantity_ui: float
    entry_time: int
    exit_time: int
    holding_seconds: int
    entry_quote_per_token: float
    exit_quote_per_token: float
    entry_quote: float
    exit_quote: float
    realized_pnl_quote: float


def reconstruct_semantic_pnl(
    swaps: Iterable[DexSwapSemanticEvidence],
) -> tuple[RealizedSemanticTrade, ...]:
    """FIFO realized PnL from explicitly promoted DEX semantic swaps.

    Only semantic evidence is accepted. This is quote-denominated PnL and does
    not convert SOL/USDC/etc. to USD. Unmatched sells are ignored rather than
    inventing an entry price.
    """
    ordered = sorted(
        (
            swap for swap in swaps
            if swap.direction in {"BUY", "SELL"}
            and swap.quantity_ui > 0
            and swap.quote_quantity_ui > 0
            and swap.price_quote_per_token > 0
            and swap.signature is not None
            and getattr(swap, "entry_time", getattr(swap, "block_time", None)) is not None
        ),
        key=lambda item: (
            getattr(item, "entry_time", getattr(item, "block_time", 0)),
            item.signature or "",
        ),
    )

    lots: dict[str, list[tuple[float, int, float]]] = {}
    result: list[RealizedSemanticTrade] = []

    for swap in ordered:
        time = getattr(swap, "entry_time", getattr(swap, "block_time", None))
        if time is None:
            continue
        if swap.direction == "BUY":
            lots.setdefault(swap.target_mint, []).append(
                (swap.quantity_ui, int(time), swap.price_quote_per_token)
            )
            continue

        remaining = swap.quantity_ui
        queue = lots.get(swap.target_mint, [])
        while remaining > 0 and queue:
            quantity, entry_time, entry_price = queue[0]
            matched = min(remaining, quantity)
            entry_quote = matched * entry_price
            exit_quote = matched * swap.price_quote_per_token
            result.append(
                RealizedSemanticTrade(
                    mint=swap.target_mint,
                    quantity_ui=matched,
                    entry_time=entry_time,
                    exit_time=int(time),
                    holding_seconds=max(0, int(time) - entry_time),
                    entry_quote_per_token=entry_price,
                    exit_quote_per_token=swap.price_quote_per_token,
                    entry_quote=entry_quote,
                    exit_quote=exit_quote,
                    realized_pnl_quote=exit_quote - entry_quote,
                )
            )
            remaining -= matched
            if matched >= quantity:
                queue.pop(0)
            else:
                queue[0] = (quantity - matched, entry_time, entry_price)

    return tuple(result)
