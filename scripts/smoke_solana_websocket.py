from __future__ import annotations

import asyncio
import pathlib
import sys
import os
import time

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.solana_stream import SolanaLogStream


def required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"{name} is required.")
    return value


async def main() -> None:
    endpoint = required("SOLANA_RPC_URL")
    mentions = os.getenv("WS_MENTIONS", "").strip() or None
    timeout_seconds = float(os.getenv("WS_TIMEOUT_SECONDS", "20"))
    stream = SolanaLogStream(
        endpoint,
        commitment=os.getenv("WS_COMMITMENT", "confirmed"),
        reconnect_delay=1.0,
    )

    started = time.perf_counter()
    print("WebSocket endpoint: derived from SOLANA_RPC_URL")
    print(f"Mentions filter: {mentions or 'all'}")
    print(f"Timeout seconds: {timeout_seconds:g}")
    print("Listening for real Solana logs...")

    iterator = stream.events(mentions=mentions).__aiter__()
    try:
        event = await asyncio.wait_for(iterator.__anext__(), timeout=timeout_seconds)
    except asyncio.TimeoutError as exc:
        raise SystemExit("RESULT: NO_EVENT_WITHIN_TIMEOUT") from exc
    finally:
        await iterator.aclose()

    elapsed_ms = (time.perf_counter() - started) * 1000.0
    print(f"EVENT_SIGNATURE: {event.signature}")
    print(f"EVENT_SLOT: {event.slot}")
    print(f"EVENT_ERROR: {event.err}")
    print(f"EVENT_LOG_COUNT: {len(event.logs)}")
    print(f"STREAM_FIRST_EVENT_MS: {elapsed_ms:.2f}")
    print("RUNTIME_PIPELINE: WEBSOCKET_EVENT_RECEIVED")


if __name__ == "__main__":
    asyncio.run(main())
