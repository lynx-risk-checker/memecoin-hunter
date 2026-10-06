from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.dexscreener import DexScreenerClient
from src.data.solana_rpc import SolanaRPCClient
from src.data.tx_parser import parse_transaction
from src.wallets.counterparties import detect_counterparty_evidence
from src.wallets.economic_links import detect_link_evidence
from src.wallets.funding import detect_shared_funding_sources, infer_funding_sources
from src.wallets.history import collect_wallet_transactions
from src.wallets.manipulation_adapter import assess_cluster_manipulation, build_cluster_manipulation_input
from src.wallets.synchronization import detect_synchronized_activity


def main() -> None:
    rpc_url = os.getenv("SOLANA_RPC_URL", "").strip()
    if not rpc_url:
        raise SystemExit("SOLANA_RPC_URL is required.")

    rpc = SolanaRPCClient(rpc_url)
    print(f"RPC health: {rpc.get_health()}")
    print(f"RPC slot: {rpc.get_slot()}")

    dex = DexScreenerClient()
    candidates = [c for c in dex.discover(max_tokens=10) if c.liquidity_usd is not None]
    if not candidates:
        raise SystemExit("No real Solana token candidate with known liquidity was returned.")

    candidate = candidates[0]
    print(f"Token: {candidate.symbol or '?'} {candidate.address}")
    print(f"Liquidity USD: {candidate.liquidity_usd}")
    print("Reading real token transaction signatures...")

    signatures = rpc.get_signatures_for_address(candidate.address, limit=20)
    parsed_transactions = []
    for item in signatures:
        signature = item.get("signature")
        if not isinstance(signature, str):
            continue
        raw = rpc.get_transaction(signature)
        if raw is None:
            continue
        try:
            parsed_transactions.append(parse_transaction(raw, signature=signature))
        except (ValueError, TypeError) as exc:
            print(f"Skipping unparseable transaction {signature[:12]}...: {exc}")

    wallets = set()
    for tx in parsed_transactions:
        for delta in tx.token_deltas:
            if delta.mint == candidate.address and delta.owner:
                wallets.add(delta.owner)

    wallets = set(sorted(wallets)[:5])
    if not wallets:
        raise SystemExit("No token-owner wallets were discovered from real transactions.")

    print(f"Candidate owner wallets discovered: {len(wallets)}")

    histories = {}
    for wallet in sorted(wallets):
        try:
            history = collect_wallet_transactions(rpc, wallet, limit=10)
        except (ValueError, RuntimeError) as exc:
            print(f"Wallet {wallet[:12]}... history failed: {exc}")
            continue
        histories[wallet] = [item.transaction for item in history]
        print(f"- {wallet}: {len(history)} real transactions parsed")

    if len(histories) < 2:
        raise SystemExit("Fewer than two wallets had usable real transaction history.")

    funding = {wallet: infer_funding_sources(wallet, txs) for wallet, txs in histories.items()}
    shared_funding = detect_shared_funding_sources(funding)
    links = detect_link_evidence(histories, min_shared_tokens=1, min_shared_transactions=1)
    synchronized = detect_synchronized_activity(histories, window_seconds=10)
    counterparties = detect_counterparty_evidence(histories)

    cluster_input = build_cluster_manipulation_input(
        wallet_count=len(histories),
        wallet_links=links,
        synchronized=synchronized,
        counterparties=counterparties,
        shared_funding=shared_funding,
    )
    manipulation = assess_cluster_manipulation(cluster_input)

    print("=== REAL WALLET INTELLIGENCE ===")
    print(f"Wallet histories: {len(histories)}")
    print(f"Economic links: {len(links)}")
    print(f"Synchronized relationships: {len(synchronized)}")
    print(f"Counterparty relationships: {len(counterparties)}")
    print(f"Shared funding relationships: {len(shared_funding)}")
    print(f"Cluster linked-wallet ratio: {cluster_input.linked_wallet_ratio:.6f}")
    print(f"Cluster synchronization ratio: {cluster_input.synchronized_entry_ratio:.6f}")
    print(f"Cluster funding-link ratio: {cluster_input.funding_link_ratio:.6f}")
    print(f"Manipulation score: {manipulation.score:.6f}")
    print(f"Manipulation blocked: {manipulation.blocked}")
    print(f"Reasons: {manipulation.reasons}")
    print("RUNTIME_PIPELINE: COMPLETED")
    print("NOTE: runtime plumbing evidence only; not proof of ownership or profitability.")


if __name__ == "__main__":
    main()
