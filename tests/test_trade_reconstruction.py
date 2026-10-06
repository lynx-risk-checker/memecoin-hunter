from src.data.tx_parser import ParsedTransaction, TokenBalanceDelta
from src.wallets.trade_reconstruction import reconstruct_trades


def _tx(sig: str, t: int, amount: int) -> ParsedTransaction:
    pre = 0 if amount >= 0 else abs(amount)
    post = amount if amount >= 0 else 0
    delta = TokenBalanceDelta("W", "MINT", 0, pre, post, 0)
    return ParsedTransaction(sig, 1, t, True, 0, (), (delta,), ())


def test_reconstructs_fifo_holding_time() -> None:
    result = reconstruct_trades(
        "W",
        [_tx("buy", 100, 100), _tx("sell", 160, -40), _tx("sell2", 220, -60)],
    )
    assert len(result) == 2
    assert result[0].quantity_ui == 40
    assert result[0].holding_seconds == 60
    assert result[1].quantity_ui == 60
    assert result[1].holding_seconds == 120


def test_ignores_failed_transactions() -> None:
    tx = _tx("failed", 100, 100)
    tx = ParsedTransaction(tx.signature, tx.slot, tx.block_time, False, tx.fee_lamports, tx.account_keys, tx.token_deltas, tx.sol_deltas)
    assert reconstruct_trades("W", [tx]) == ()
