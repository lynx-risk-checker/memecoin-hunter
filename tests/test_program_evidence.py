from src.data.tx_parser import AccountKey, ParsedTransaction, TokenBalanceDelta
from src.wallets.program_evidence import classify_program_evidence


def test_classifies_known_program_with_target_flow() -> None:
    tx = ParsedTransaction(
        "sig",
        1,
        100,
        True,
        0,
        (AccountKey("SWAP_PROGRAM", False, False),),
        (TokenBalanceDelta("W", "TARGET", 0, 0, 100, 0),),
        (),
    )
    result = classify_program_evidence(
        "W",
        [tx],
        target_mint="TARGET",
        known_swap_program_ids=["SWAP_PROGRAM"],
    )
    assert len(result) == 1
    assert result[0].direction == "BUY"
    assert result[0].evidence_class == "KNOWN_PROGRAM_PLUS_TOKEN_FLOW"


def test_unknown_program_is_not_claimed_as_swap() -> None:
    tx = ParsedTransaction(
        "sig",
        1,
        100,
        True,
        0,
        (AccountKey("OTHER_PROGRAM", False, False),),
        (TokenBalanceDelta("W", "TARGET", 0, 0, 100, 0),),
        (),
    )
    assert classify_program_evidence(
        "W",
        [tx],
        target_mint="TARGET",
        known_swap_program_ids=["SWAP_PROGRAM"],
    ) == ()
