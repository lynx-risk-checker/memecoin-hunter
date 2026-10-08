from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any, AsyncIterator, Callable
from urllib.parse import urlparse, urlunparse

import websockets


class SolanaWebSocketError(RuntimeError):
    """Raised when a Solana WebSocket stream cannot be established."""


@dataclass(frozen=True)
class SolanaLogEvent:
    subscription_id: int
    signature: str
    slot: int
    err: Any
    logs: tuple[str, ...]


def websocket_endpoint(http_endpoint: str) -> str:
    parsed = urlparse(http_endpoint.strip())
    if parsed.scheme == "https":
        scheme = "wss"
    elif parsed.scheme == "http":
        scheme = "ws"
    elif parsed.scheme in {"ws", "wss"}:
        scheme = parsed.scheme
    else:
        raise ValueError("Solana RPC endpoint must use http(s), ws, or wss.")
    return urlunparse((scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))


def parse_logs_notification(message: str | bytes) -> SolanaLogEvent:
    if isinstance(message, bytes):
        message = message.decode("utf-8")
    try:
        body = json.loads(message)
    except json.JSONDecodeError as exc:
        raise SolanaWebSocketError("Invalid WebSocket JSON message.") from exc

    params = body.get("params")
    if not isinstance(params, dict):
        raise SolanaWebSocketError("WebSocket notification is missing params.")
    result = params.get("result")
    if not isinstance(result, dict):
        raise SolanaWebSocketError("WebSocket notification is missing result.")
    value = result.get("value")
    context = result.get("context")
    if not isinstance(value, dict) or not isinstance(context, dict):
        raise SolanaWebSocketError("WebSocket notification has invalid result shape.")
    signature = value.get("signature")
    slot = context.get("slot")
    logs = value.get("logs")
    subscription_id = params.get("subscription")
    if not isinstance(signature, str) or not signature:
        raise SolanaWebSocketError("WebSocket notification has no signature.")
    if not isinstance(slot, int) or slot < 0:
        raise SolanaWebSocketError("WebSocket notification has invalid slot.")
    if not isinstance(subscription_id, int) or subscription_id < 0:
        raise SolanaWebSocketError("WebSocket notification has invalid subscription id.")
    if logs is None:
        logs_tuple: tuple[str, ...] = ()
    elif isinstance(logs, list) and all(isinstance(item, str) for item in logs):
        logs_tuple = tuple(logs)
    else:
        raise SolanaWebSocketError("WebSocket notification has invalid logs.")
    return SolanaLogEvent(
        subscription_id=subscription_id,
        signature=signature,
        slot=slot,
        err=value.get("err"),
        logs=logs_tuple,
    )


class SolanaLogStream:
    """Read-only logsSubscribe stream.

    This emits signatures quickly; full transaction parsing remains the responsibility
    of SolanaRPCClient.get_transaction(). It never submits a transaction or order.
    """

    def __init__(
        self,
        endpoint: str,
        *,
        commitment: str = "confirmed",
        ping_interval: float = 20.0,
        reconnect_delay: float = 2.0,
        websocket_factory: Callable[..., Any] | None = None,
    ) -> None:
        if not endpoint.strip():
            raise ValueError("Solana RPC endpoint is required.")
        if commitment not in {"processed", "confirmed", "finalized"}:
            raise ValueError("Unsupported Solana commitment.")
        if ping_interval <= 0 or reconnect_delay < 0:
            raise ValueError("Invalid stream timing.")
        self.endpoint = endpoint
        self.commitment = commitment
        self.ping_interval = ping_interval
        self.reconnect_delay = reconnect_delay
        self._websocket_factory = websocket_factory or websockets.connect

    async def events(self, *, mentions: str | None = None) -> AsyncIterator[SolanaLogEvent]:
        if mentions is not None and not mentions.strip():
            raise ValueError("mentions cannot be empty.")
        request_id = 1
        params: list[Any] = [{"commitment": self.commitment}]
        if mentions:
            params[0]["mentions"] = [mentions]

        while True:
            try:
                async with self._websocket_factory(
                    websocket_endpoint(self.endpoint),
                    ping_interval=self.ping_interval,
                ) as websocket:
                    await websocket.send(json.dumps({
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "method": "logsSubscribe",
                        "params": ["all", params[0]],
                    }))
                    request_id += 1

                    subscription = json.loads(await websocket.recv())
                    if "error" in subscription:
                        raise SolanaWebSocketError(
                            f"logsSubscribe failed: {subscription['error']}"
                        )

                    while True:
                        raw = await websocket.recv()
                        event = parse_logs_notification(raw)
                        yield event
            except asyncio.CancelledError:
                raise
            except (OSError, TimeoutError, SolanaWebSocketError):
                if self.reconnect_delay:
                    await asyncio.sleep(self.reconnect_delay)
