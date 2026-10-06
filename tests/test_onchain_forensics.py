from src.data.tx_parser import ParsedTransaction, TokenBalanceDelta
from src.forensics.onchain import infer_token_flow, summarize_five_minutes


def _tx(sig: str, t: int, owner: str, raw: int) -> ParsedTransaction:
    delta = TokenBalanceDelta(owner, "MINT", 0, 0 if raw > 0 else -raw, raw if raw > 0 else 0, 0)
    return ParsedTransaction(sig, 1, t, True, 0, (), (delta,), ())


def test_native_five_minute_flow_uses_transaction_block_time() -> None:
    flows = infer_token_flow([_tx("a", 1000, "buyer", 5), _tx("b", 1100, "seller", -3)], token_mint="MINT")
    result = summarize_five_minutes(flows, end_time=1100)
    assert result.transactions == 2
    assert result.buy_volume_ui == 5
    assert result.sell_volume_ui == 3
    assert result.unique_buyers == 1
    assert result.unique_sellers == 1
