from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# Allow this script to import the repository's top-level `src` package when
# invoked as `python scripts/<script>.py`.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.dexscreener import DexScreenerClient
from src.forensics.collector import ForensicsCollector
from src.forensics.window import summarize_five_minute


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

    interval = float(os.getenv("FORENSICS_INTERVAL_SECONDS", "60"))
    observations = int(os.getenv("FORENSICS_OBSERVATIONS", "6"))
    if interval <= 0:
        raise ValueError("FORENSICS_INTERVAL_SECONDS must be positive.")
    if observations < 2:
        raise ValueError("FORENSICS_OBSERVATIONS must be at least 2.")

    print(f"Token: {token_address}")
    print(
        f"Collecting {observations} real observations at {interval:g}s intervals "
        f"(target window <= 5 minutes)..."
    )

    for index in range(observations):
        print(f"Observation {index + 1}/{observations}: collecting real DEX data...")
        collector.observe(token_address)
        if index + 1 < observations:
            print(f"Waiting {interval:g}s before next observation...")
            time.sleep(interval)

    summary = summarize_five_minute(collector.history(token_address))
    if summary is None:
        raise RuntimeError("Five-minute forensic summary was not produced.")

    print("=== FIVE-MINUTE FORENSICS ===")
    print(f"Observation count: {summary.observation_count}")
    print(f"Elapsed seconds: {summary.elapsed_seconds:.3f}")
    print(f"Price change %: {summary.price_change_pct:.6f}")
    print(f"Liquidity change %: {summary.liquidity_change_pct:.6f}")
    print(f"Volume change %: {summary.volume_change_pct:.6f}")
    print(f"Buy count change: {summary.buy_count_change}")
    print(f"Sell count change: {summary.sell_count_change}")
    print(f"Buy/sell ratio: {summary.buy_sell_ratio}")
    print(f"Volume rate/min: {summary.volume_rate_per_minute:.6f}")
    print(f"Buy rate/min: {summary.buy_rate_per_minute:.6f}")
    print(f"Sell rate/min: {summary.sell_rate_per_minute:.6f}")
    print(f"Volume acceleration %: {summary.volume_acceleration_pct}")
    print(f"Buy acceleration %: {summary.buy_acceleration_pct}")
    print(f"Sell acceleration %: {summary.sell_acceleration_pct}")
    print(f"Unique buyer change: {summary.unique_buyer_change}")
    print(f"Unique seller change: {summary.unique_seller_change}")
    print(f"Holder change: {summary.holder_change}")
    print(f"Market cap change %: {summary.market_cap_change_pct}")
    print(f"Data complete: {summary.data_complete}")


if __name__ == "__main__":
    main()
