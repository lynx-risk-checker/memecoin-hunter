from src.data.tx_parser import ParsedTransaction, SolBalanceDelta, TokenBalanceDelta
from src.wallets.swap_evidence import SwapEvidence, extract_balance_flow_swaps


def _tx(target: int, quote: int) -> ParsedTransaction:
    target_delta = TokenBalanceDelta("W", "TARGET", 0, 0, target, 0)
    return ParsedTransaction(
        "sig",
        1,
        100,
        True,
        0,
        (),
        (target_delta,),
        (SolBalanceDelta("W", 0, 10_000_000_000, 9_000_000_000),)
        if quote < 0
        else (SolBalanceDelta("W", 0, 9_000_000_000, 10_000_000_000),),
    )


def test_infers_buy_price_from_token_and_sol_balance_flow() -> None:
    result = extract_balance_flow_swaps("W", [_tx(100, -1)], target_mint="TARGET", quote_mint="SOL")
    assert len(result) == 1
    assert result[0].direction == "BUY"
    assert result[0].quote_quantity_ui == 1.0
    assert result[0].price_quote_per_token == 0.01
    assert result[0].price_usd is None
    assert result[0].evidence_class == "BALANCE_FLOW_ACCOUNTING"


def test_usd_price_is_not_inferred_from_sol_denominated_quote() -> None:
    evidence = SwapEvidence(
        signature="sig",
        mint="TARGET",
        quantity_ui=100.0,
        quote_mint="SOL",
        quote_quantity_ui=1.0,
        price_quote_per_token=0.01,
        block_time=100,
        direction="BUY",
        evidence_class="BALANCE_FLOW_ACCOUNTING",
    )
    assert evidence.price_usd is None


def test_stablecoin_quote_can_be_exposed_as_usd_proxy() -> None:
    evidence = SwapEvidence(
        signature="sig",
        mint="TARGET",
        quantity_ui=100.0,
        quote_mint="USDC",
        quote_quantity_ui=1.0,
        price_quote_per_token=0.01,
        block_time=100,
        direction="BUY",
        evidence_class="BALANCE_FLOW_ACCOUNTING",
    )
    assert evidence.price_usd == 0.01


def test_ignores_non_swap_like_flow() -> None:
    result = extract_balance_flow_swaps("W", [_tx(100, 1)], target_mint="TARGET", quote_mint="USDC")
    assert result == ()


def test_canonical_solana_usdc_mint_is_recognized_as_usd_proxy() -> None:
    evidence = SwapEvidence(
        signature="sig",
        mint="TARGET",
        quantity_ui=100.0,
        quote_mint="EPjFWdd5AufqSSqeM2q8xzybapC8G4wEGGkZwyTDt1v",
        quote_quantity_ui=1.0,
        price_quote_per_token=0.01,
        block_time=100,
        direction="BUY",
        evidence_class="BALANCE_FLOW_ACCOUNTING",
    )
    assert evidence.price_usd == 0.01


def test_canonical_solana_usdt_mint_is_recognized_as_usd_proxy() -> None:
    evidence = SwapEvidence(
        signature="sig",
        mint="TARGET",
        quantity_ui=100.0,
        quote_mint="Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
        quote_quantity_ui=1.0,
        price_quote_per_token=0.01,
        block_time=100,
        direction="BUY",
        evidence_class="BALANCE_FLOW_ACCOUNTING",
    )
    assert evidence.price_usd == 0.01
