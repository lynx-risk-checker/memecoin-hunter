from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.data.instruction_parser import InstructionEvidence, extract_instruction_evidence
from src.data.tx_parser import ParsedTransaction


@dataclass(frozen=True)
class DexProgramSpec:
    """Explicit, operator-supplied semantics for one DEX/aggregator program.

    No program ID or discriminator is guessed by this module. A spec is only
    authoritative for the exact identifiers supplied by the caller.
    """

    name: str
    program_ids: frozenset[str]
    parsed_types: frozenset[str] = frozenset()
    data_prefixes: frozenset[str] = frozenset()

    def matches(self, evidence: InstructionEvidence) -> bool:
        if evidence.program_id not in self.program_ids:
            return False
        if self.parsed_types and evidence.parsed_type in self.parsed_types:
            return True
        if self.data_prefixes and evidence.data:
            return any(evidence.data.startswith(prefix) for prefix in self.data_prefixes)
        if not self.parsed_types and not self.data_prefixes:
            return True
        return False


@dataclass(frozen=True)
class DexSwapSemanticEvidence:
    signature: str | None
    dex_name: str
    program_id: str
    source: str
    instruction_index: int | None
    parent_index: int | None
    direction: str
    target_mint: str
    quote_mint: str
    quantity_ui: float
    quote_quantity_ui: float
    price_quote_per_token: float
    semantic_class: str
    block_time: int | None


def classify_dex_swap_semantics(
    *,
    transaction: ParsedTransaction,
    raw_transaction: dict,
    swap: object,
    specs: Iterable[DexProgramSpec],
) -> tuple[DexSwapSemanticEvidence, ...]:
    """Promote balance-flow evidence only when explicit DEX semantics match.

    The swap object must expose direction, mint, quote_mint, quantity_ui,
    quote_quantity_ui, and price_quote_per_token. The function deliberately
    accepts the existing SwapEvidence without importing it, avoiding a cycle.
    """
    signature = getattr(swap, "signature", None)
    if signature != transaction.signature or not transaction.success:
        return ()
    direction = getattr(swap, "direction", None)
    target_mint = getattr(swap, "mint", None)
    quote_mint = getattr(swap, "quote_mint", None)
    quantity = getattr(swap, "quantity_ui", None)
    quote_quantity = getattr(swap, "quote_quantity_ui", None)
    price = getattr(swap, "price_quote_per_token", None)
    if (
        direction not in {"BUY", "SELL"}
        or not isinstance(target_mint, str)
        or not isinstance(quote_mint, str)
        or not all(isinstance(value, (int, float)) and value > 0 for value in (quantity, quote_quantity, price))
    ):
        return ()

    instructions = extract_instruction_evidence(raw_transaction)
    result: list[DexSwapSemanticEvidence] = []
    seen: set[tuple[str | None, str, str, str]] = set()
    for spec in specs:
        for evidence in instructions:
            if not spec.matches(evidence):
                continue
            # Balance-flow evidence is transaction-level. Multiple matching
            # inner/outer instructions in the same transaction must not create
            # duplicate economic swaps for downstream PnL.
            key = (transaction.signature, spec.name, direction, target_mint)
            if key in seen:
                continue
            seen.add(key)
            result.append(
                DexSwapSemanticEvidence(
                    signature=transaction.signature,
                    dex_name=spec.name,
                    program_id=evidence.program_id,
                    source=evidence.source,
                    instruction_index=evidence.instruction_index,
                    parent_index=evidence.parent_index,
                    direction=direction,
                    target_mint=target_mint,
                    quote_mint=quote_mint,
                    quantity_ui=float(quantity),
                    quote_quantity_ui=float(quote_quantity),
                    price_quote_per_token=float(price),
                    semantic_class=(
                        "EXPLICIT_PROGRAM_SEMANTICS_PLUS_BALANCE_FLOW"
                        if spec.parsed_types or spec.data_prefixes
                        else "EXPLICIT_PROGRAM_ID_PLUS_BALANCE_FLOW"
                    ),
                    block_time=transaction.block_time,
                )
            )
    return tuple(result)
