from __future__ import annotations

from dataclasses import dataclass

from src.manipulation import ManipulationAssessment, assess_manipulation
from src.wallets.counterparties import CounterpartyEvidence
from src.wallets.economic_links import WalletLinkEvidence
from src.wallets.funding import SharedFundingEvidence
from src.wallets.synchronization import SynchronizedActivity


@dataclass(frozen=True)
class ClusterManipulationInput:
    linked_wallet_ratio: float
    synchronized_entry_ratio: float
    holder_concentration_ratio: float
    dev_sell_ratio: float
    funding_link_ratio: float


def _ratio(count: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return min(1.0, max(0.0, count / denominator))


def build_cluster_manipulation_input(
    *,
    wallet_count: int,
    wallet_links: tuple[WalletLinkEvidence, ...] = (),
    synchronized: tuple[SynchronizedActivity, ...] = (),
    counterparties: tuple[CounterpartyEvidence, ...] = (),
    shared_funding: tuple[SharedFundingEvidence, ...] = (),
    holder_concentration_ratio: float = 0.0,
    dev_sell_ratio: float = 0.0,
) -> ClusterManipulationInput:
    if wallet_count < 0:
        raise ValueError("wallet_count must be non-negative")
    if not 0 <= holder_concentration_ratio <= 1 or not 0 <= dev_sell_ratio <= 1:
        raise ValueError("ratio inputs must be between 0 and 1")

    pair_capacity = max(wallet_count * (wallet_count - 1) // 2, 1)
    # Counterparty links are deliberately folded into linked-wallet evidence only
    # through their own count; they remain separately observable by callers.
    linked_count = max(len(wallet_links), len(counterparties))
    return ClusterManipulationInput(
        linked_wallet_ratio=_ratio(linked_count, pair_capacity),
        synchronized_entry_ratio=max(
            (item.synchronization_ratio for item in synchronized), default=0.0
        ),
        holder_concentration_ratio=holder_concentration_ratio,
        dev_sell_ratio=dev_sell_ratio,
        funding_link_ratio=max(
            (item.confidence for item in shared_funding), default=0.0
        ),
    )


def assess_cluster_manipulation(
    inputs: ClusterManipulationInput,
    *,
    threshold: float = 0.70,
) -> ManipulationAssessment:
    return assess_manipulation(
        linked_wallet_ratio=inputs.linked_wallet_ratio,
        synchronized_entry_ratio=inputs.synchronized_entry_ratio,
        holder_concentration_ratio=inputs.holder_concentration_ratio,
        dev_sell_ratio=inputs.dev_sell_ratio,
        funding_link_ratio=inputs.funding_link_ratio,
        threshold=threshold,
    )
