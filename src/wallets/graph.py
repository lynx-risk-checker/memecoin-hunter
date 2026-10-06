from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .models import WalletObservation


@dataclass(frozen=True)
class WalletGraph:
    wallet_to_tokens: dict[str, frozenset[str]]
    token_to_wallets: dict[str, frozenset[str]]


def build_graph(observations: list[WalletObservation]) -> WalletGraph:
    wallet_to_tokens: dict[str, set[str]] = defaultdict(set)
    token_to_wallets: dict[str, set[str]] = defaultdict(set)
    for item in observations:
        wallet_to_tokens[item.wallet].add(item.token)
        token_to_wallets[item.token].add(item.wallet)
    return WalletGraph(
        wallet_to_tokens={k: frozenset(v) for k, v in wallet_to_tokens.items()},
        token_to_wallets={k: frozenset(v) for k, v in token_to_wallets.items()},
    )


def shared_token_overlap(
    graph: WalletGraph, wallet_a: str, wallet_b: str
) -> int:
    return len(graph.wallet_to_tokens.get(wallet_a, frozenset())
               & graph.wallet_to_tokens.get(wallet_b, frozenset()))
