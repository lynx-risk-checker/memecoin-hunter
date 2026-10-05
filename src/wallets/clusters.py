from __future__ import annotations

from dataclasses import dataclass

from .graph import WalletGraph


@dataclass(frozen=True)
class ClusterLink:
    wallet_a: str
    wallet_b: str
    shared_tokens: int
    confidence: float


def detect_overlap_links(
    graph: WalletGraph,
    *,
    min_shared_tokens: int = 2,
    min_confidence: float = 0.5,
) -> tuple[ClusterLink, ...]:
    if min_shared_tokens < 1:
        raise ValueError("min_shared_tokens must be positive")
    if not 0 <= min_confidence <= 1:
        raise ValueError("min_confidence must be between 0 and 1")

    wallets = sorted(graph.wallet_to_tokens)
    links: list[ClusterLink] = []
    for index, wallet_a in enumerate(wallets):
        for wallet_b in wallets[index + 1:]:
            shared = len(
                graph.wallet_to_tokens[wallet_a]
                & graph.wallet_to_tokens[wallet_b]
            )
            if shared < min_shared_tokens:
                continue
            union = graph.wallet_to_tokens[wallet_a] | graph.wallet_to_tokens[wallet_b]
            confidence = shared / len(union) if union else 0.0
            if confidence >= min_confidence:
                links.append(ClusterLink(wallet_a, wallet_b, shared, confidence))
    return tuple(links)
