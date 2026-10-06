from src.data.tx_parser import (
    AccountKey,
    ParsedTransaction,
    SolBalanceDelta,
    TokenBalanceDelta,
)
from src.wallets.supported_swap_evidence import classify_supported_swap_evidence


def test_joins_known_program_instruction_with_balance_flow() -> None:
    parsed = ParsedTransaction(
        signature="SIG1",
        slot=10,
        block_time=100,
        success=True,
        fee_lamports=5000,
        account_keys=(AccountKey("WALLET", True, True), AccountKey("PROGRAM_A", False, False)),
        token_deltas=(
            TokenBalanceDelta("WALLET", "TARGET", 2, 0, 1000, 0),
        ),
        sol_deltas=(
            SolBalanceDelta("WALLET", 0, 2_000_000_000, 1_000_000_000),
        ),
    )
    raw = {
        "transaction": {
            "signatures": ["SIG1"],
            "message": {
                "accountKeys": ["WALLET", "PROGRAM_A"],
                "instructions": [
                    {"programId": "PROGRAM_A", "accounts": [0]}
                ],
            },
        },
        "meta": {"innerInstructions": []},
    }

    result = classify_supported_swap_evidence(
        "WALLET",
        [parsed],
        [raw],
        target_mint="TARGET",
        quote_mint="SOL",
        known_swap_program_ids=["PROGRAM_A"],
    )

    assert len(result) == 1
    assert result[0].direction == "BUY"
    assert result[0].quantity_ui == 1000
    assert result[0].quote_quantity_ui == 0.999995
    assert result[0].price_quote_per_token == 0.000999995
    assert result[0].network_fee_quote == 0.000005
    assert result[0].evidence_class == "KNOWN_PROGRAM_PLUS_BALANCE_FLOW"


def test_known_program_without_balance_flow_is_not_called_swap_evidence() -> None:
    parsed = ParsedTransaction(
        signature="SIG2",
        slot=11,
        block_time=101,
        success=True,
        fee_lamports=5000,
        account_keys=(AccountKey("WALLET", True, True), AccountKey("PROGRAM_A", False, False)),
        token_deltas=(),
        sol_deltas=(),
    )
    raw = {
        "transaction": {
            "signatures": ["SIG2"],
            "message": {
                "accountKeys": ["WALLET", "PROGRAM_A"],
                "instructions": [{"programId": "PROGRAM_A"}],
            },
        }
    }

    result = classify_supported_swap_evidence(
        "WALLET",
        [parsed],
        [raw],
        target_mint="TARGET",
        quote_mint="SOL",
        known_swap_program_ids=["PROGRAM_A"],
    )
    assert result == ()


def test_unknown_program_is_not_promoted() -> None:
    parsed = ParsedTransaction(
        signature="SIG3",
        slot=12,
        block_time=102,
        success=True,
        fee_lamports=5000,
        account_keys=(AccountKey("WALLET", True, True),),
        token_deltas=(
            TokenBalanceDelta("WALLET", "TARGET", 1, 0, 100, 0),
        ),
        sol_deltas=(
            SolBalanceDelta("WALLET", 0, 2_000_000_000, 1_000_000_000),
        ),
    )
    raw = {
        "transaction": {
            "signatures": ["SIG3"],
            "message": {
                "accountKeys": ["WALLET", "UNKNOWN_PROGRAM"],
                "instructions": [{"programId": "UNKNOWN_PROGRAM"}],
            },
        }
    }

    result = classify_supported_swap_evidence(
        "WALLET",
        [parsed],
        [raw],
        target_mint="TARGET",
        quote_mint="SOL",
        known_swap_program_ids=["PROGRAM_A"],
    )
    assert result == ()
