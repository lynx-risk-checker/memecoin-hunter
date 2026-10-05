from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class SolanaRPCError(RuntimeError):
    """Raised when a Solana JSON-RPC request cannot be completed."""


@dataclass
class SolanaRPCClient:
    endpoint: str
    timeout_seconds: float = 10.0

    def __post_init__(self) -> None:
        if not self.endpoint.strip():
            raise ValueError("Solana RPC endpoint is required.")

    def call(self, method: str, params: list[Any] | None = None) -> Any:
        payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": [] if params is None else params}
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise SolanaRPCError(f"Solana RPC request failed: {method}") from exc
        if "error" in body:
            raise SolanaRPCError(f"Solana RPC error for {method}: {body['error']}")
        return body.get("result")

    def get_health(self) -> str:
        return str(self.call("getHealth"))

    def get_slot(self) -> int:
        return int(self.call("getSlot"))

    def get_block_height(self) -> int:
        return int(self.call("getBlockHeight"))

    def get_signatures_for_address(
        self, address: str, *, limit: int = 10, before: str | None = None,
        until: str | None = None, commitment: str = "confirmed",
    ) -> list[dict[str, Any]]:
        if not address.strip():
            raise ValueError("Address is required.")
        if not 1 <= limit <= 1000:
            raise ValueError("limit must be between 1 and 1000.")
        config: dict[str, Any] = {"limit": limit, "commitment": commitment}
        if before is not None:
            config["before"] = before
        if until is not None:
            config["until"] = until
        result = self.call("getSignaturesForAddress", [address, config])
        if not isinstance(result, list):
            raise SolanaRPCError("Invalid getSignaturesForAddress result.")
        return result

    def get_transaction(
        self, signature: str, *, commitment: str = "confirmed",
        max_supported_transaction_version: int = 1, encoding: str = "jsonParsed",
    ) -> dict[str, Any] | None:
        if not signature.strip():
            raise ValueError("Transaction signature is required.")
        result = self.call("getTransaction", [signature, {
            "commitment": commitment,
            "maxSupportedTransactionVersion": max_supported_transaction_version,
            "encoding": encoding,
        }])
        if result is not None and not isinstance(result, dict):
            raise SolanaRPCError("Invalid getTransaction result.")
        return result
