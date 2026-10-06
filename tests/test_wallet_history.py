from __future__ import annotations

from src.wallets.history import collect_wallet_transactions


class FakeRPC:
    def get_signatures_for_address(self, address, *, limit=10, before=None, until=None, commitment="confirmed"):
        return [
            {"signature": "sig-a", "slot": 10},
            {"signature": "sig-b", "slot": 11},
            {"slot": 12},
        ]

    def get_transaction(self, signature, *, commitment="confirmed", max_supported_transaction_version=1, encoding="jsonParsed"):
        if signature == "sig-b":
            return None
        return {
            "slot": 10,
            "blockTime": 1_700_000_000,
            "meta": {
                "err": None,
                "fee": 5_000,
                "preBalances": [2_000_000_000],
                "postBalances": [1_999_000_000],
                "preTokenBalances": [],
                "postTokenBalances": [],
            },
            "transaction": {
                "signatures": [signature],
                "message": {"accountKeys": ["Wallet111"]},
            },
        }


def test_collect_wallet_transactions_resolves_signatures_to_transactions() -> None:
    result = collect_wallet_transactions(FakeRPC(), "Wallet111", limit=3)

    assert len(result) == 1
    assert result[0].signature == "sig-a"
    assert result[0].transaction.sol_deltas[0].sol_delta == -0.001
