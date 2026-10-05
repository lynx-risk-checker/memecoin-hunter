from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from src.data.tx_parser import ParsedTransaction


@dataclass(frozen=True)
class FundingEvidence:
    wallet: str
    source_accounts: tuple[str, ...]
    source_count: int
    confidence: float


def infer_funding_sources(
    wallet: str,
    transactions: list[ParsedTransaction],
    *,
    max_sources: int = 20,
) -> FundingEvidence:
    if not wallet.strip():
        raise ValueError("wallet is required")
    if max_sources <= 0:
        raise ValueError("max_sources must be positive")

    sources: set[str] = set()
    for tx in transactions:
        if not tx.success:
            continue
        # Only use explicit account keys. This identifies candidate counterparties;
        # it does not prove that a counterparty funded the wallet.
        for key in tx.account_keys:
            if key.pubkey != wallet:
                sources.add(key.pubkey)

    ordered = tuple(sorted(sources)[:max_sources])
    confidence = min(1.0, len(ordered) / 5.0)
    return FundingEvidence(wallet, ordered, len(ordered), confidence)


@dataclass(frozen=True)
class SharedFundingEvidence:
    wallet_a: str
    wallet_b: str
    shared_sources: int
    confidence: float


def detect_shared_funding_sources(
    evidence: dict[str, FundingEvidence],
) -> tuple[SharedFundingEvidence, ...]:
    result: list[SharedFundingEvidence] = []
    for wallet_a, wallet_b in combinations(sorted(evidence), 2):
        shared = set(evidence[wallet_a].source_accounts) & set(evidence[wallet_b].source_accounts)
        if not shared:
            continue
        confidence = min(1.0, len(shared) / 3.0)
        result.append(
            SharedFundingEvidence(wallet_a, wallet_b, len(shared), confidence)
        )
    return tuple(result)
