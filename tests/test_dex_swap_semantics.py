from src.data.tx_parser import AccountKey, ParsedTransaction, TokenBalanceDelta
from src.wallets.dex_swap_semantics import DexProgramSpec, classify_dex_swap_semantics
from src.wallets.swap_evidence import SwapEvidence


PROGRAM = "DexProgram11111111111111111111111111111111"
WALLET = "Wallet111111111111111111111111111111111111"
TOKEN = "Token111111111111111111111111111111111111"
QUOTE = "Quote111111111111111111111111111111111111"


def _tx() -> ParsedTransaction:
    return ParsedTransaction(
        signature="sig",
        slot=1,
        block_time=100,
        success=True,
        fee_lamports=5000,
        account_keys=(AccountKey(WALLET, True, True), AccountKey(PROGRAM, False, False)),
        token_deltas=(
            TokenBalanceDelta(WALLET, TOKEN, 0, 0, 1000, 0),
            TokenBalanceDelta(WALLET, QUOTE, 0, 1000, 0, 0),
        ),
        sol_deltas=(),
    )


def _raw(parsed_type="swap", data=None):
    instruction = {
        "programId": PROGRAM,
        "parsed": {"type": parsed_type},
        "accounts": [],
    }
    if data is not None:
        instruction.pop("parsed")
        instruction["data"] = data
    return {
        "slot": 1,
        "blockTime": 100,
        "transaction": {
            "signatures": ["sig"],
            "message": {
                "accountKeys": [WALLET, PROGRAM],
                "instructions": [instruction],
            },
        },
        "meta": {"err": None, "innerInstructions": [], "logMessages": []},
    }


def _swap():
    return SwapEvidence(
        signature="sig",
        mint=TOKEN,
        quantity_ui=1000,
        quote_mint="SOL",
        quote_quantity_ui=1,
        price_quote_per_token=0.001,
        block_time=100,
        direction="BUY",
        evidence_class="BALANCE_FLOW_ACCOUNTING",
    )


def test_explicit_program_and_parsed_type_promotes_evidence():
    spec = DexProgramSpec("TestDEX", frozenset({PROGRAM}), frozenset({"swap"}))
    result = classify_dex_swap_semantics(
        transaction=_tx(), raw_transaction=_raw(), swap=_swap(), specs=(spec,)
    )
    assert len(result) == 1
    assert result[0].semantic_class == "EXPLICIT_PROGRAM_SEMANTICS_PLUS_BALANCE_FLOW"


def test_unknown_program_does_not_promote():
    spec = DexProgramSpec("OtherDEX", frozenset({"OtherProgram"}), frozenset({"swap"}))
    assert classify_dex_swap_semantics(
        transaction=_tx(), raw_transaction=_raw(), swap=_swap(), specs=(spec,)
    ) == ()


def test_explicit_data_prefix_can_promote():
    spec = DexProgramSpec("TestDEX", frozenset({PROGRAM}), data_prefixes=frozenset({"AA"}))
    result = classify_dex_swap_semantics(
        transaction=_tx(), raw_transaction=_raw(parsed_type=None, data="AABBCC"), swap=_swap(), specs=(spec,)
    )
    assert len(result) == 1


def test_program_only_spec_is_explicit_and_not_a_guess():
    spec = DexProgramSpec("TestDEX", frozenset({PROGRAM}))
    result = classify_dex_swap_semantics(
        transaction=_tx(), raw_transaction=_raw(), swap=_swap(), specs=(spec,)
    )
    assert len(result) == 1


def test_multiple_matching_instructions_do_not_duplicate_transaction_evidence():
    raw = _raw()
    raw["transaction"]["message"]["instructions"].append(
        {"programId": PROGRAM, "parsed": {"type": "swap"}, "accounts": []}
    )
    spec = DexProgramSpec("TestDEX", frozenset({PROGRAM}), frozenset({"swap"}))
    result = classify_dex_swap_semantics(
        transaction=_tx(), raw_transaction=raw, swap=_swap(), specs=(spec,)
    )
    assert len(result) == 1


def test_failed_transaction_does_not_promote_dex_semantics():
    raw = _raw()
    raw["meta"]["err"] = {"InstructionError": [0, "Custom"]}
    failed = ParsedTransaction(
        signature="sig",
        slot=1,
        block_time=100,
        success=False,
        fee_lamports=5000,
        account_keys=(AccountKey(WALLET, True, True), AccountKey(PROGRAM, False, False)),
        token_deltas=(
            TokenBalanceDelta(WALLET, TOKEN, 0, 0, 1000, 0),
            TokenBalanceDelta(WALLET, QUOTE, 0, 1000, 0, 0),
        ),
        sol_deltas=(),
    )
    spec = DexProgramSpec("TestDEX", frozenset({PROGRAM}), frozenset({"swap"}))
    assert classify_dex_swap_semantics(
        transaction=failed, raw_transaction=raw, swap=_swap(), specs=(spec,)
    ) == ()
