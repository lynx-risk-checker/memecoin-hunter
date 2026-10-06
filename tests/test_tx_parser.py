from __future__ import annotations

import pytest

from src.data.tx_parser import parse_transaction


def _transaction() -> dict:
    return {
        "slot": 42,
        "blockTime": 1_700_000_000,
        "meta": {
            "err": None,
            "fee": 5_000,
            "preBalances": [2_000_000_000, 1_000_000],
            "postBalances": [1_999_000_000, 1_001_000],
            "preTokenBalances": [
                {
                    "accountIndex": 1,
                    "mint": "Mint111",
                    "owner": "Wallet111",
                    "uiTokenAmount": {"amount": "10", "decimals": 2},
                }
            ],
            "postTokenBalances": [
                {
                    "accountIndex": 1,
                    "mint": "Mint111",
                    "owner": "Wallet111",
                    "uiTokenAmount": {"amount": "35", "decimals": 2},
                }
            ],
        },
        "transaction": {
            "signatures": ["Sig111"],
            "message": {
                "accountKeys": [
                    {"pubkey": "Wallet111", "signer": True, "source": "transaction", "writable": True},
                    {"pubkey": "Vault111", "signer": False, "source": "transaction", "writable": True},
                ]
            },
        },
    }


def test_parse_transaction_extracts_explicit_balance_deltas() -> None:
    result = parse_transaction(_transaction())

    assert result.signature == "Sig111"
    assert result.slot == 42
    assert result.success is True
    assert result.fee_lamports == 5_000
    assert result.token_deltas[0].owner == "Wallet111"
    assert result.token_deltas[0].raw_delta == 25
    assert result.token_deltas[0].ui_delta == 0.25
    assert result.sol_deltas[0].account == "Wallet111"
    assert result.sol_deltas[0].sol_delta == -0.001


def test_parse_transaction_handles_new_token_account() -> None:
    tx = _transaction()
    tx["meta"]["preTokenBalances"] = []
    result = parse_transaction(tx)

    assert result.token_deltas[0].raw_delta == 35


def test_parse_transaction_rejects_misaligned_sol_balances() -> None:
    tx = _transaction()
    tx["meta"]["postBalances"] = [1]

    with pytest.raises(ValueError, match="align"):
        parse_transaction(tx)


def test_parse_transaction_does_not_infer_buy_or_sell() -> None:
    result = parse_transaction(_transaction())

    assert result.token_deltas[0].raw_delta > 0
    assert not hasattr(result.token_deltas[0], "side")


def test_parse_transaction_includes_versioned_loaded_addresses() -> None:
    tx = _transaction()
    tx["transaction"]["message"]["accountKeys"] = [
        {
            "pubkey": "StaticWallet",
            "signer": True,
            "source": "transaction",
            "writable": True,
        }
    ]
    tx["meta"]["loadedAddresses"] = {
        "writable": ["LoadedWritable"],
        "readonly": ["LoadedReadonly"],
    }
    tx["meta"]["preBalances"] = [2_000_000_000, 1_000_000, 2_000_000]
    tx["meta"]["postBalances"] = [1_999_000_000, 1_001_000, 2_000_000]

    result = parse_transaction(tx)

    assert [item.pubkey for item in result.account_keys] == [
        "StaticWallet",
        "LoadedWritable",
        "LoadedReadonly",
    ]
    assert result.sol_deltas[0].account == "StaticWallet"
