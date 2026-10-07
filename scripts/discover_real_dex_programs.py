from __future__ import annotations

import os
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.solana_rpc import SolanaRPCClient
from src.data.instruction_parser import extract_instruction_evidence
from src.data.tx_parser import parse_transaction
from src.wallets.swap_evidence import extract_balance_flow_swaps


def required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"{name} is required.")
    return value


def main() -> None:
    rpc = SolanaRPCClient(required("SOLANA_RPC_URL"))
    wallet = required("WALLET_ADDRESS")
    target_mint = required("TARGET_MINT")
    quote_mint = required("QUOTE_MINT")
    limit = int(os.getenv("TX_LIMIT", "100"))
    if not 1 <= limit <= 1000:
        raise SystemExit("TX_LIMIT must be between 1 and 1000.")

    print(f"RPC health: {rpc.get_health()}")
    print(f"RPC slot: {rpc.get_slot()}")
    print(f"Wallet: {wallet}")
    print(f"Target mint: {target_mint}")
    print(f"Quote mint: {quote_mint}")
    print("Reading confirmed real transactions...")

    signatures = rpc.get_signatures_for_address(wallet, limit=limit, commitment="confirmed")
    candidates = []
    program_counts: Counter[str] = Counter()
    parsed_count = 0

    for item in signatures:
        signature = item.get("signature")
        if not isinstance(signature, str):
            continue
        raw = rpc.get_transaction(signature, commitment="confirmed")
        if raw is None:
            continue
        try:
            tx = parse_transaction(raw, signature=signature)
        except (ValueError, TypeError):
            continue
        parsed_count += 1
        if not tx.success:
            continue
        swaps = extract_balance_flow_swaps(
            wallet,
            (tx,),
            target_mint=target_mint,
            quote_mint=quote_mint,
        )
        if not swaps:
            continue
        instructions = extract_instruction_evidence(raw)
        programs = tuple(dict.fromkeys(e.program_id for e in instructions))
        for program in programs:
            program_counts[program] += 1
        candidates.append((signature, swaps, instructions))

    print(f"Confirmed transactions parsed: {parsed_count}")
    print(f"Balance-flow swap transactions: {len(candidates)}")
    print("Evidence rule: only successful transactions are eligible for discovery.")

    if not candidates:
        print("RESULT: NO_BALANCE_FLOW_SWAP_CANDIDATES")
        return

    print("--- CANDIDATE PROGRAM DISCOVERY ---")
    for signature, swaps, instructions in candidates:
        print(f"Signature: {signature}")
        print("Directions:", ",".join(sorted({s.direction for s in swaps})))
        print("Programs observed:")
        for program in sorted({e.program_id for e in instructions}):
            matching = [e for e in instructions if e.program_id == program]
            types = sorted({e.parsed_type for e in matching if e.parsed_type})
            print(f"  {program} | instruction_count={len(matching)} | parsed_types={types or ['<none>']}")
        print("  NOTE: observed program != proven DEX semantics")

    print("--- PROGRAM FREQUENCY ACROSS CANDIDATES ---")
    for program, count in program_counts.most_common():
        print(f"{program} | candidate_transactions={count}")

    print("RESULT: REAL_TRANSACTION_PROGRAM_DISCOVERY_COMPLETE")
    print("No program was promoted to DEX semantics by this discovery script.")


if __name__ == "__main__":
    main()
