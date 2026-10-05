from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from src.data.tx_parser import ParsedTransaction


@dataclass(frozen=True)
class WalletLinkEvidence:
    wallet_a: str
    wallet_b: str
    shared_tokens: int
    shared_transactions: int
    confidence: float


def _token_sets(transactions: dict[str, list[ParsedTransaction]]) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for wallet, items in transactions.items():
        result[wallet] = {delta.mint for item in items for delta in item.token_deltas}
    return result


def _shared_transactions(
    wallet_a: str,
    wallet_b: str,
    transactions: dict[str, list[ParsedTransaction]],
) -> int:
    a = {item.signature for item in transactions.get(wallet_a, ()) if item.signature}
    b = {item.signature for item in transactions.get(wallet_b, ()) if item.signature}
    return len(a & b)


def detect_link_evidence(
    transactions: dict[str, list[ParsedTransaction]],
    *,
    min_shared_tokens: int = 2,
    min_shared_transactions: int = 1,
) -> tuple[WalletLinkEvidence, ...]:
    if min_shared_tokens < 1 or min_shared_transactions < 1:
        raise ValueError("minimum evidence thresholds must be positive")
    wallets = sorted(transactions)
    token_sets = _token_sets(transactions)
    links: list[WalletLinkEvidence] = []
    for wallet_a, wallet_b in combinations(wallets, 2):
        shared_tokens = len(token_sets.get(wallet_a, set()) & token_sets.get(wallet_b, set()))
        shared_transactions = _shared_transactions(wallet_a, wallet_b, transactions)
        if shared_tokens < min_shared_tokens and shared_transactions < min_shared_transactions:
            continue
        token_union = token_sets.get(wallet_a, set()) | token_sets.get(wallet_b, set())
        token_similarity = shared_tokens / len(token_union) if token_union else 0.0
        transaction_signal = min(shared_transactions / 3.0, 1.0)
        confidence = 0.5 * token_similarity + 0.5 * transaction_signal
        links.append(WalletLinkEvidence(wallet_a, wallet_b, shared_tokens, shared_transactions, confidence))
    return tuple(links)
