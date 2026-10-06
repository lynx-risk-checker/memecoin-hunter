from src.data.tx_parser import ParsedTransaction
from src.wallets.dex_swap_semantics import DexProgramSpec, classify_dex_swap_semantics


class Swap:
    signature = 'sig'
    direction = 'BUY'
    mint = 'TOKEN'
    quote_mint = 'SOL'
    quantity_ui = 10.0
    quote_quantity_ui = 1.0
    price_quote_per_token = 0.1
    block_time = 1


def test_program_only_is_not_called_full_semantics():
    tx = ParsedTransaction('sig', 1, 1, True, 1, (), (), ())
    raw = {'transaction': {'message': {'accountKeys': ['DEX'], 'instructions': [{'programId': 'DEX'}]}}}
    result = classify_dex_swap_semantics(
        transaction=tx,
        raw_transaction=raw,
        swap=Swap(),
        specs=(DexProgramSpec('ExampleDEX', frozenset({'DEX'})),),
    )
    assert result[0].semantic_class == 'EXPLICIT_PROGRAM_ID_PLUS_BALANCE_FLOW'


def test_parsed_type_is_full_semantic_evidence():
    tx = ParsedTransaction('sig', 1, 1, True, 1, (), (), ())
    raw = {'transaction': {'message': {'accountKeys': ['DEX'], 'instructions': [{'programId': 'DEX', 'parsed': {'type': 'swap'}}]}}}
    result = classify_dex_swap_semantics(
        transaction=tx,
        raw_transaction=raw,
        swap=Swap(),
        specs=(DexProgramSpec('ExampleDEX', frozenset({'DEX'}), parsed_types=frozenset({'swap'})),),
    )
    assert result[0].semantic_class == 'EXPLICIT_PROGRAM_SEMANTICS_PLUS_BALANCE_FLOW'
