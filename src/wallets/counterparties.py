from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from src.data.tx_parser import ParsedTransaction


@dataclass(frozen=True)
class CounterpartyEvidence:
    wallet_a: str
    wallet_b: str
    shared_counterparties: int
    shared_mints: int
    confidence: float


def _counterparties(wallet: str, tx: ParsedTransaction) -> set[str]:
    accounts = {key.pubkey for key in tx.account_keys if key.pubkey != wallet}
    return accounts


def detect_counterparty_evidence(
    transactions: dict[str, list[ParsedTransaction]],
) -> tuple[CounterpartyEvidence, ...]:
    wallets = sorted(transactions)
    result: list[CounterpartyEvidence] = []
    for wallet_a, wallet_b in combinations(wallets, 2):
        counterparties_a: set[str] = set()
        counterparties_b: set[str] = set()
        mints_a: set[str] = set()
        mints_b: set[str] = set()

        for tx in transactions[wallet_a]:
            counterparties_a.update(_counterparties(wallet_a, tx))
            mints_a.update(delta.mint for delta in tx.token_deltas)
        for tx in transactions[wallet_b]:
            counterparties_b.update(_counterparties(wallet_b, tx))
            mints_b.update(delta.mint for delta in tx.token_deltas)

        shared_counterparties = len(counterparties_a & counterparties_b)
        shared_mints = len(mints_a & mints_b)
        if not shared_counterparties and not shared_mints:
            continue

        # Evidence is intentionally conservative: shared counterparties are
        # stronger than simple shared-token history, but are not proof of ownership.
        confidence = min(
            1.0,
            0.70 * min(shared_counterparties / 3.0, 1.0)
            + 0.30 * min(shared_mints / 3.0, 1.0),
        )
        result.append(
            CounterpartyEvidence(
                wallet_a,
                wallet_b,
                shared_counterparties,
                shared_mints,
                confidence,
            )
        )
    return tuple(result)
