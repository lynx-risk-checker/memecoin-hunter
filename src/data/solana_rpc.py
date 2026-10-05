from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class SolanaRPCError(RuntimeError):
    """Raised when a Solana JSON-RPC request cannot be completed."""


@dataclass(frozen=True)
class SolanaRPCClient:
    endpoint: str
    timeout_seconds: float = 10.0

    def __post_init__(self) -> None:
        if not self.endpoint.strip():
            raise ValueError("Solana RPC endpoint is required.")

    def call(self, method: str, params: list[Any] | None = None) -> Any:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": [] if params is None else params,
        }
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
