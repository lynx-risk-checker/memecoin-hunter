from src.wallets.dex_swap_semantics import DexSwapSemanticEvidence
from src.wallets.semantic_pnl import reconstruct_semantic_pnl


def swap(direction, qty, price, time, sig):
    return DexSwapSemanticEvidence(
        signature=sig,
        dex_name="ExampleDEX",
        program_id="DEX",
        source="outer",
        instruction_index=0,
        parent_index=None,
        direction=direction,
        target_mint="TOKEN",
        quote_mint="SOL",
        quantity_ui=qty,
        quote_quantity_ui=qty * price,
        price_quote_per_token=price,
        semantic_class="EXPLICIT_PROGRAM_SEMANTICS_PLUS_BALANCE_FLOW",
        block_time=time,
    )


def test_fifo_realized_pnl_from_semantic_swaps():
    result = reconstruct_semantic_pnl([
        swap("BUY", 100, 0.01, 100, "b"),
        swap("BUY", 50, 0.02, 200, "b2"),
        swap("SELL", 120, 0.03, 300, "s"),
    ])
    assert len(result) == 2
    assert result[0].quantity_ui == 100
    assert result[0].realized_pnl_quote == 2.0
    assert result[1].quantity_ui == 20
    assert result[1].realized_pnl_quote == 0.2


def test_unmatched_sell_does_not_invent_entry():
    result = reconstruct_semantic_pnl([swap("SELL", 100, 0.03, 300, "s")])
    assert result == ()
