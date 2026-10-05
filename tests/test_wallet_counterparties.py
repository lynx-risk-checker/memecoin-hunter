from __future__ import annotations

from src.data.tx_parser import parse_transaction
from src.wallets.counterparties import detect_counterparty_evidence


def _tx(sig: str, mint: str) -> dict:
    return {
        "slot": 1,
        "blockTime": 100,
        "meta": {
            "err": None,
            "fee": 5000,
            "preBalances": [100, 50],
            "postBalances": [90, 50],
            "preTokenBalances": [{
                "accountIndex": 0,
                "mint": mint,
                "owner": "OWNER",
                "uiTokenAmount": {"amount": "0", "decimals": 0},
            }],
            "postTokenBalances": [{
                "accountIndex": 0,
                "mint": mint,
                "owner": "OWNER",
                "uiTokenAmount": {"amount": "1", "decimals": 0},
            }],
        },
        "transaction": {
            "signatures": [sig],
            "message": {
                "accountKeys": ["OWNER", "COMMON_COUNTERPARTY"],
            },
        },
    }


def test_detect_counterparty_evidence() -> None:
    result = detect_counterparty_evidence({
        "A": [parse_transaction(_tx("a", "MINT"))],
        "B": [parse_transaction(_tx("b", "MINT"))],
    })
    assert len(result) == 1
    assert result[0].shared_counterparties == 1
    assert result[0].shared_mints == 1
    assert 0 < result[0].confidence <= 1
