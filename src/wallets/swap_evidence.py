from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.data.tx_parser import ParsedTransaction


@dataclass(frozen=True)
class SwapEvidence:
    signature: str | None
    mint: str
    quantity_ui: float
    quote_mint: str
    quote_quantity_ui: float
    price_quote_per_token: float
    block_time: int | None
    direction: str
    evidence_class: str

    @property
    def price_usd(self) -> float | None:
        return self.price_quote_per_token if self.quote_mint in {"SOL", "USDC", "USDT"} else None


def extract_balance_flow_swaps(
    wallet: str,
    transactions: Iterable[ParsedTransaction],
    *,
    target_mint: str,
    quote_mint: str,
) -> tuple[SwapEvidence, ...]:
    if not wallet.strip():
        raise ValueError("wallet is required")
    if not target_mint.strip() or not quote_mint.strip():
        raise ValueError("target_mint and quote_mint are required")
    if target_mint == quote_mint:
        raise ValueError("target_mint and quote_mint must differ")

    result: list[SwapEvidence] = []
    for tx in transactions:
        if not tx.success:
            continue

        target_delta = sum(
            d.ui_delta
            for d in tx.token_deltas
            if d.owner == wallet and d.mint == target_mint
        )
        quote_delta = sum(
            d.ui_delta
            for d in tx.token_deltas
            if d.owner == wallet and d.mint == quote_mint
        )

        # SOL is represented separately from SPL token balances.
        if quote_mint == "SOL":
            quote_delta = sum(
                d.sol_delta for d in tx.sol_deltas if d.account == wallet
            )

        if target_delta == 0 or quote_delta == 0:
            continue

        if target_delta > 0 and quote_delta < 0:
            direction = "BUY"
        elif target_delta < 0 and quote_delta > 0:
            direction = "SELL"
        else:
            continue

        quantity = abs(target_delta)
        quote_quantity = abs(quote_delta)
        result.append(
            SwapEvidence(
                signature=tx.signature,
                mint=target_mint,
                quantity_ui=quantity,
                quote_mint=quote_mint,
                quote_quantity_ui=quote_quantity,
                price_quote_per_token=quote_quantity / quantity,
                block_time=tx.block_time,
                direction=direction,
                evidence_class="BALANCE_FLOW_INFERRED",
            )
        )

    return tuple(result)
