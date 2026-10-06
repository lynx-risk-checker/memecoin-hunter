from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data.solana_rpc import SolanaRPCClient
from src.data.tx_parser import parse_transaction
from src.wallets.dex_swap_semantics import DexProgramSpec, classify_dex_swap_semantics
from src.wallets.swap_evidence import extract_balance_flow_swaps


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"{name} is required.")
    return value


def main() -> None:
    rpc_url = _required("SOLANA_RPC_URL")
    wallet = _required("WALLET_ADDRESS")
    target_mint = _required("TARGET_MINT")
    quote_mint = _required("QUOTE_MINT")
    dex_name = _required("DEX_NAME")

    program_ids = frozenset(
        item.strip()
        for item in _required("DEX_PROGRAM_IDS").split(",")
        if item.strip()
    )
    if not program_ids:
        raise SystemExit("DEX_PROGRAM_IDS must contain at least one explicit program ID.")

    parsed_types = frozenset(
        item.strip()
        for item in os.getenv("DEX_PARSED_TYPES", "").split(",")
        if item.strip()
    )
    data_prefixes = frozenset(
        item.strip()
        for item in os.getenv("DEX_DATA_PREFIXES", "").split(",")
        if item.strip()
    )
    limit = int(os.getenv("TX_LIMIT", "50"))
    if not 1 <= limit <= 1000:
        raise SystemExit("TX_LIMIT must be between 1 and 1000.")

    spec = DexProgramSpec(
        name=dex_name,
        program_ids=program_ids,
        parsed_types=parsed_types,
        data_prefixes=data_prefixes,
    )

    rpc = SolanaRPCClient(rpc_url)
    print(f"RPC health: {rpc.get_health()}")
    print(f"RPC slot: {rpc.get_slot()}")
    print(f"Wallet: {wallet}")
    print(f"Target mint: {target_mint}")
    print(f"Quote mint: {quote_mint}")
    print(f"Explicit DEX: {dex_name}")
    print(f"Explicit program IDs: {sorted(program_ids)}")
    print("Reading confirmed real transactions...")

    signatures = rpc.get_signatures_for_address(wallet, limit=limit, commitment="confirmed")
    parsed = []
    raw_by_signature: dict[str, dict] = {}

    for item in signatures:
        signature = item.get("signature")
        if not isinstance(signature, str):
            continue
        raw = rpc.get_transaction(signature, commitment="confirmed")
        if raw is None:
            continue
        try:
            tx = parse_transaction(raw, signature=signature)
        except (ValueError, TypeError) as exc:
            print(f"Skipping unparseable transaction {signature[:12]}...: {exc}")
            continue
        parsed.append(tx)
        raw_by_signature[signature] = raw

    print(f"Confirmed transactions parsed: {len(parsed)}")

    flow_swaps = extract_balance_flow_swaps(
        wallet,
        parsed,
        target_mint=target_mint,
        quote_mint=quote_mint,
    )
    print(f"Balance-flow swap candidates: {len(flow_swaps)}")

    semantic = []
    for swap in flow_swaps:
        raw = raw_by_signature.get(swap.signature)
        tx = next((item for item in parsed if item.signature == swap.signature), None)
        if raw is None or tx is None:
            continue
        semantic.extend(
            classify_dex_swap_semantics(
                transaction=tx,
                raw_transaction=raw,
                swap=swap,
                specs=(spec,),
            )
        )

    print(f"Explicit DEX semantic matches: {len(semantic)}")
    for item in semantic:
        print("--- CONFIRMED SEMANTIC CANDIDATE ---")
        print(f"Signature: {item.signature}")
        print(f"DEX: {item.dex_name}")
        print(f"Program ID: {item.program_id}")
        print(f"Instruction source: {item.source}")
        print(f"Direction: {item.direction}")
        print(f"Target quantity: {item.quantity_ui}")
        print(f"Quote quantity: {item.quote_quantity_ui}")
        print(f"Execution price ({item.quote_mint}/token): {item.price_quote_per_token}")
        print(f"Evidence class: {item.semantic_class}")

    if not semantic:
        print("RESULT: NO_CONFIRMED_DEX_SEMANTIC_MATCH")
        print("No DEX swap is promoted without the explicit program specification.")
    else:
        print("RESULT: REAL_CONFIRMED_DEX_SEMANTIC_MATCHES_FOUND")
        print("NOTE: semantic match is not yet a realized-PnL ground truth; fee/rent/other balance movements and route-level accounting still require validation.")


if __name__ == "__main__":
    main()
