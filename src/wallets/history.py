from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from src.data.solana_rpc import SolanaRPCClient
from src.data.tx_parser import ParsedTransaction, parse_transaction


class TransactionReader(Protocol):
    def get_signatures_for_address(
        self, address: str, *, limit: int = 10, before: str | None = None,
        until: str | None = None, commitment: str = "confirmed",
    ) -> list[dict[str, Any]]: ...

    def get_transaction(
        self, signature: str, *, commitment: str = "confirmed",
        max_supported_transaction_version: int = 1,
        encoding: str = "jsonParsed",
    ) -> dict[str, Any] | None: ...


@dataclass(frozen=True)
class WalletTransaction:
    signature: str
    slot: int | None
    transaction: ParsedTransaction


def collect_wallet_transactions(
    client: TransactionReader,
    wallet: str,
    *,
    limit: int = 10,
) -> tuple[WalletTransaction, ...]:
    if not wallet.strip():
        raise ValueError("wallet is required")
    if not 1 <= limit <= 1000:
        raise ValueError("limit must be between 1 and 1000")

    signatures = client.get_signatures_for_address(wallet, limit=limit)
    result: list[WalletTransaction] = []
    for item in signatures:
        signature = item.get("signature")
        if not isinstance(signature, str) or not signature.strip():
            continue
        transaction = client.get_transaction(signature)
        if transaction is None:
            continue
        parsed = parse_transaction(transaction, signature=signature)
        result.append(WalletTransaction(signature=signature, slot=item.get("slot"), transaction=parsed))
    return tuple(result)
