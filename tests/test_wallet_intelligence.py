from src.data.tx_parser import ParsedTransaction, TokenBalanceDelta
from src.wallets.intelligence import build_wallet_intelligence


def _tx(sig: str, owner: str, mint: str, raw_delta: int) -> ParsedTransaction:
    pre = 0 if raw_delta >= 0 else abs(raw_delta)
    post = raw_delta if raw_delta >= 0 else 0
    delta = TokenBalanceDelta(
        owner=owner,
        mint=mint,
        account_index=0,
        pre_amount=pre,
        post_amount=post,
        decimals=0,
    )
    return ParsedTransaction(sig, 1, 1000, True, 0, (), (delta,), ())


def test_build_wallet_intelligence_aggregates_wallet_token_flow() -> None:
    result = build_wallet_intelligence(
        "WALLET",
        [_tx("a", "WALLET", "MINT", 100), _tx("b", "WALLET", "MINT", -40)],
    )
    assert result.transactions == 2
    assert result.token_stats[0].buys == 1
    assert result.token_stats[0].sells == 1
    assert result.token_stats[0].bought_ui == 100.0
    assert result.token_stats[0].sold_ui == 40.0
    assert result.token_stats[0].net_flow_ui == 60.0


def test_build_wallet_intelligence_ignores_other_wallets() -> None:
    assert build_wallet_intelligence(
        "WALLET",
        [_tx("a", "OTHER", "MINT", 100)],
    ).token_stats == ()
