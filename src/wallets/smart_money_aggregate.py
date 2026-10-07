from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.wallets.economic_links import WalletLinkEvidence
from src.wallets.independence import assess_wallet_independence
from src.wallets.smart_money import SmartMoneyAssessment


@dataclass(frozen=True)
class SmartMoneyAggregate:
    wallet_count: int
    independent_cluster_count: int
    independence_ratio: float
    effective_support: float
    average_reliability: float
    pnl_evidence_wallets: int


def aggregate_smart_money(
    assessments: Iterable[SmartMoneyAssessment],
    links: Iterable[WalletLinkEvidence] = (),
) -> SmartMoneyAggregate:
    """Aggregate wallet quality without double-counting linked wallets.

    Each connected economic cluster contributes its strongest wallet
    assessment, rather than allowing every correlated wallet to stack the
    signal. This is a conservative heuristic, not ownership proof.
    """
    items = tuple(assessments)
    if not items:
        return SmartMoneyAggregate(0, 0, 0.0, 0.0, 0.0, 0)

    wallets = tuple(item.wallet for item in items)
    independence = assess_wallet_independence(wallets, links)

    parent = {wallet: wallet for wallet in wallets}

    def find(wallet: str) -> str:
        root = wallet
        while parent[root] != root:
            root = parent[root]
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

    best_by_cluster: dict[str, SmartMoneyAssessment] = {}
    for item in items:
        root = find(item.wallet)
        current = best_by_cluster.get(root)
        if current is None or item.reliability_score > current.reliability_score:
            best_by_cluster[root] = item

    selected = tuple(best_by_cluster.values())
    effective_support = (
        sum(item.reliability_score for item in selected) / len(selected)
        if selected else 0.0
    )
    average_reliability = (
        sum(item.reliability_score for item in items) / len(items)
        if items else 0.0
    )

    return SmartMoneyAggregate(
        wallet_count=len(wallets),
        independent_cluster_count=independence.cluster_count,
        independence_ratio=independence.independence_ratio,
        effective_support=effective_support,
        average_reliability=average_reliability,
        pnl_evidence_wallets=sum(item.pnl_evidence_available for item in selected),
    )
