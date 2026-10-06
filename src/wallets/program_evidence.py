from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.data.tx_parser import ParsedTransaction


@dataclass(frozen=True)
class ProgramEvidence:
    signature: str | None
    program_ids: tuple[str, ...]
    target_mint: str
    direction: str
    block_time: int | None
    evidence_class: str


def classify_program_evidence(
    wallet: str,
    transactions: Iterable[ParsedTransaction],
    *,
    target_mint: str,
    known_swap_program_ids: Iterable[str],
) -> tuple[ProgramEvidence, ...]:
    """Classify transactions with known swap-program accounts plus target-token flow.

    This is intentionally conservative: the current ParsedTransaction model exposes
    account keys but not compiled instruction payloads. Therefore this layer only
    labels program-account presence as supporting evidence, never as proof that a
    swap instruction executed.
    """
    if not wallet.strip():
        raise ValueError("wallet is required")
    if not target_mint.strip():
        raise ValueError("target_mint is required")

    known = {x.strip() for x in known_swap_program_ids if x.strip()}
    if not known:
        return ()

    result: list[ProgramEvidence] = []
    for tx in transactions:
        if not tx.success:
            continue

        program_ids = tuple(
            key.pubkey for key in tx.account_keys if key.pubkey in known
        )
        if not program_ids:
            continue

        target_delta = sum(
            d.ui_delta
            for d in tx.token_deltas
            if d.owner == wallet and d.mint == target_mint
        )
        if target_delta > 0:
            direction = "BUY"
        elif target_delta < 0:
            direction = "SELL"
        else:
            continue

        result.append(
            ProgramEvidence(
                signature=tx.signature,
                program_ids=program_ids,
                target_mint=target_mint,
                direction=direction,
                block_time=tx.block_time,
                evidence_class="KNOWN_PROGRAM_PLUS_TOKEN_FLOW",
            )
        )

    return tuple(result)
