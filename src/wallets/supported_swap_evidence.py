from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.data.instruction_parser import extract_instruction_evidence
from src.data.tx_parser import ParsedTransaction
from src.wallets.swap_evidence import extract_balance_flow_swaps


@dataclass(frozen=True)
class SupportedSwapEvidence:
    signature: str | None
    mint: str
    quote_mint: str
    quantity_ui: float
    quote_quantity_ui: float
    price_quote_per_token: float
    block_time: int | None
    direction: str
    program_ids: tuple[str, ...]
    evidence_class: str


def classify_supported_swap_evidence(
    wallet: str,
    transactions: Iterable[ParsedTransaction],
    raw_transactions: Iterable[dict],
    *,
    target_mint: str,
    quote_mint: str,
    known_swap_program_ids: Iterable[str],
) -> tuple[SupportedSwapEvidence, ...]:
    """Join balance-flow evidence with observable known-program instruction evidence.

    This is intentionally not named or described as definitive swap proof. A
    known program can appear in a transaction for reasons other than the target
    swap, so execution semantics still require DEX-specific decoding.
    """
    known = {item.strip() for item in known_swap_program_ids if item.strip()}
    if not known:
        return ()

    parsed_by_signature = {
        tx.signature: tx
        for tx in transactions
        if tx.signature is not None
    }
    raw_by_signature = {}
    for raw in raw_transactions:
        if not isinstance(raw, dict):
            continue
        tx = raw.get("transaction")
        signatures = tx.get("signatures") if isinstance(tx, dict) else None
        if isinstance(signatures, list) and signatures and isinstance(signatures[0], str):
            raw_by_signature[signatures[0]] = raw

    result: list[SupportedSwapEvidence] = []
    for flow in extract_balance_flow_swaps(
        wallet,
        parsed_by_signature.values(),
        target_mint=target_mint,
        quote_mint=quote_mint,
    ):
        raw = raw_by_signature.get(flow.signature)
        if raw is None:
            continue

        instructions = extract_instruction_evidence(raw)
        program_ids = tuple(dict.fromkeys(
            evidence.program_id
            for evidence in instructions
            if evidence.program_id in known
        ))
        if not program_ids:
            continue

        result.append(
            SupportedSwapEvidence(
                signature=flow.signature,
                mint=flow.mint,
                quote_mint=flow.quote_mint,
                quantity_ui=flow.quantity_ui,
                quote_quantity_ui=flow.quote_quantity_ui,
                price_quote_per_token=flow.price_quote_per_token,
                block_time=flow.block_time,
                direction=flow.direction,
                program_ids=program_ids,
                evidence_class="KNOWN_PROGRAM_PLUS_BALANCE_FLOW",
            )
        )

    return tuple(result)
