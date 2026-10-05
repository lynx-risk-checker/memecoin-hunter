from __future__ import annotations

import os

from src.data.dexscreener import DexScreenerClient
from src.data.solana_rpc import SolanaRPCClient


def main() -> None:
    rpc_url = os.getenv("SOLANA_RPC_URL", "").strip()
    if not rpc_url:
        raise SystemExit("SOLANA_RPC_URL is required for the Solana RPC smoke test.")

    rpc = SolanaRPCClient(rpc_url)
    print(f"RPC health: {rpc.get_health()}")
    print(f"RPC slot: {rpc.get_slot()}")

    dex = DexScreenerClient()
    candidates = dex.discover(max_tokens=10)
    print(f"DEX Screener Solana candidates: {len(candidates)}")

    for candidate in candidates[:5]:
        print(
            f"- {candidate.symbol or '?'} "
            f"{candidate.address} "
            f"liquidity_usd={candidate.liquidity_usd} "
            f"market_cap_usd={candidate.market_cap_usd} "
            f"age_seconds={candidate.age_seconds}"
        )


if __name__ == "__main__":
    main()
