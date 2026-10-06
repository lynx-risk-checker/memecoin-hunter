from __future__ import annotations

from dataclasses import dataclass

from src.data.tx_parser import ParsedTransaction


@dataclass(frozen=True)
class DevBehavior:
    wallet: str
    transactions: int
    token_inflows: int
    token_outflows: int
    successful_transactions: int
    token_outflow_ratio: float
    status: str


def assess_dev_behavior(wallet: str, transactions: list[ParsedTransaction]) -> DevBehavior:
    if not wallet.strip():
        raise ValueError("wallet is required")
    successful = sum(item.success for item in transactions)
    inflows = 0
    outflows = 0
    for transaction in transactions:
        for delta in transaction.token_deltas:
            if delta.owner != wallet:
                continue
            if delta.raw_delta > 0:
                inflows += 1
            elif delta.raw_delta < 0:
                outflows += 1
    total = inflows + outflows
    ratio = outflows / total if total else 0.0
    if total == 0:
        status = "NO_TOKEN_ACTIVITY"
    elif ratio >= 0.70:
        status = "OUTFLOW_HEAVY"
    elif ratio <= 0.30:
        status = "INFLOW_HEAVY"
    else:
        status = "MIXED"
    return DevBehavior(wallet, len(transactions), inflows, outflows, successful, ratio, status)
