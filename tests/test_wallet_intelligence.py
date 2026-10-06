from src.data.tx_parser import ParsedTransaction, TokenBalanceDelta
from src.wallets.intelligence import build_wallet_intelligence


def _tx(sig: str, owner: str, mint: str, raw_delta: int, ui_delta: float) -> ParsedTransaction:
    delta = TokenBalanceDelta(
        mint=mint,
        owner=owner,
        account_index=0,
        raw_delta=raw_delta,
        ui_delta=ui_delta,
    )
    return ParsedTransaction(sig, 1, 1000, True, 0, (), (delta,), ())


def test_build_wallet_intelligence_aggregates_wallet_token_flow() -> None:
    result = build_wallet_intelligence(
        "WALLET",
        [
            _tx("a", "WALLET", "MINT", 100, 10.0),
            _tx("b", "WALLET", "MINT", -40, -4.0),
        ],
    )
    assert result.transactions == 2
    assert result.successful_transactions == 2
    assert result.token_stats[0].buys == 1
    assert result.token_stats[0].sells == 1
    assert result.token_stats[0].bought_ui == 10.0
    assert result.token_stats[0].sold_ui == 4.0
    assert result.token_stats[0].net_flow_ui == 6.0
    assert result.activity_score > 0


def test_build_wallet_intelligence_ignores_other_wallets() -> None:
    result = build_wallet_intelligence(
        "WALLET",
        [_tx("a", "OTHER", "MINT", 100, 10.0)],
    )
    assert result.token_stats == ()
