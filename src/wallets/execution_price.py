from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionPrice:
    quantity_ui: float
    quote_quantity_ui: float
    quote_mint: str
    price_quote_per_token: float
    network_fee_quote: float
    accounting_class: str


def derive_execution_price(
    *,
    quantity_ui: float,
    quote_delta_ui: float,
    quote_mint: str,
    fee_lamports: int = 0,
) -> ExecutionPrice | None:
    """Derive a conservative balance-based execution price.

    For native SOL, the wallet balance delta includes the transaction fee, so
    the fee is removed before estimating the swap quote amount. This does not
    remove rent/other SOL movements, therefore the result remains
    BALANCE_FLOW_ACCOUNTING rather than definitive DEX execution semantics.
    """
    if quantity_ui <= 0:
        raise ValueError("quantity_ui must be positive")
    if quote_delta_ui == 0:
        return None
    if fee_lamports < 0:
        raise ValueError("fee_lamports must be non-negative")

    fee_quote = fee_lamports / 1_000_000_000 if quote_mint == "SOL" else 0.0

    if quote_delta_ui < 0:
        # Quote spent by wallet. For SOL, network fee is also part of the
        # negative wallet balance delta and must not be counted as swap spend.
        quote_quantity = abs(quote_delta_ui)
        if quote_mint == "SOL":
            quote_quantity = max(0.0, quote_quantity - fee_quote)
    else:
        # Quote received by wallet; no network-fee subtraction.
        quote_quantity = quote_delta_ui

    if quote_quantity <= 0:
        return None

    return ExecutionPrice(
        quantity_ui=quantity_ui,
        quote_quantity_ui=quote_quantity,
        quote_mint=quote_mint,
        price_quote_per_token=quote_quantity / quantity_ui,
        network_fee_quote=fee_quote,
        accounting_class="BALANCE_FLOW_ACCOUNTING",
    )
