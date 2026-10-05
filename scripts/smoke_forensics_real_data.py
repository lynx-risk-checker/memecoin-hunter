from __future__ import annotations

import os
import time

from src.data.dexscreener import DexScreenerClient
from src.forensics.collector import ForensicsCollector


def main() -> None:
    client = DexScreenerClient()
    collector = ForensicsCollector(client)

    token_address = os.getenv("TOKEN_ADDRESS", "").strip()
    if not token_address:
        candidates = client.discover(max_tokens=10)
        candidates = [c for c in candidates if c.liquidity_usd is not None]
        if not candidates:
            raise RuntimeError("No Solana candidate with known liquidity was returned.")
        token_address = candidates[0].address

    interval = float(os.getenv("FORENSICS_INTERVAL_SECONDS", "5"))
    if interval <= 0:
        raise ValueError("FORENSICS_INTERVAL_SECONDS must be positive.")

    print(f"Token: {token_address}")
    print("Observation 1: collecting real DEX data...")
    collector.observe(token_address)

    print(f"Waiting {interval:g}s before observation 2...")
    time.sleep(interval)

    print("Observation 2: collecting real DEX data...")
    collector.observe(token_address)

    delta = collector.latest_delta(token_address)
    if delta is None:
        raise RuntimeError("Forensic delta was not produced.")

    print(f"Elapsed seconds: {delta.elapsed_seconds:.3f}")
    print(f"Price change %: {delta.price_change_pct:.6f}")
    print(f"Liquidity change %: {delta.liquidity_change_pct:.6f}")
    print(f"Volume change %: {delta.volume_change_pct:.6f}")
    print(f"Buy count change: {delta.buy_count_change}")
    print(f"Sell count change: {delta.sell_count_change}")
    print(f"Unique buyer change: {delta.unique_buyer_change}")
    print(f"Holder change: {delta.holder_change}")


if __name__ == "__main__":
    main()
