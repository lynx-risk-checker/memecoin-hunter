from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WalletObservation:
    wallet: str
    token: str
    side: str
    amount_usd: float
    observed_at: float

    def __post_init__(self) -> None:
        if not self.wallet.strip() or not self.token.strip():
            raise ValueError("wallet and token are required")
        if self.side not in {"BUY", "SELL"}:
            raise ValueError("side must be BUY or SELL")
        if self.amount_usd <= 0:
            raise ValueError("amount_usd must be positive")


@dataclass(frozen=True)
class WalletCluster:
    cluster_id: str
    wallets: tuple[str, ...]
    confidence: float

    def __post_init__(self) -> None:
        if not self.cluster_id.strip() or not self.wallets:
            raise ValueError("cluster_id and wallets are required")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
