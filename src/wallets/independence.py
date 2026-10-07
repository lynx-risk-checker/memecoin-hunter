from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.wallets.economic_links import WalletLinkEvidence


@dataclass(frozen=True)
class IndependenceAssessment:
    wallet_count: int
    cluster_count: int
    independence_ratio: float
    effective_wallet_count: float


def assess_wallet_independence(
    wallets: Iterable[str],
    links: Iterable[WalletLinkEvidence],
) -> IndependenceAssessment:
    """Estimate independent wallet groups using observed economic links.

    This is a conservative graph heuristic, not proof of common ownership.
    Any observed link joins two wallets into the same connected component.
    """
    unique_wallets = tuple(dict.fromkeys(wallets))
    if not unique_wallets:
        return IndependenceAssessment(0, 0, 0.0, 0.0)

    parent = {wallet: wallet for wallet in unique_wallets}

    def find(wallet: str) -> str:
        root = wallet
        while parent[root] != root:
            root = parent[root]
        while parent[wallet] != wallet:
            next_wallet = parent[wallet]
            parent[wallet] = root
            wallet = next_wallet
        return root

    def union(left: str, right: str) -> None:
        if left not in parent or right not in parent or left == right:
            return
        left_root = find(left)
        right_root = find(right)
        if left_root != right_root:
            parent[right_root] = left_root

    for link in links:
        union(link.wallet_a, link.wallet_b)

    cluster_count = len({find(wallet) for wallet in unique_wallets})
    wallet_count = len(unique_wallets)
    ratio = cluster_count / wallet_count
    return IndependenceAssessment(
        wallet_count=wallet_count,
        cluster_count=cluster_count,
        independence_ratio=ratio,
        effective_wallet_count=float(cluster_count),
    )
