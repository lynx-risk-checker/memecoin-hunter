from __future__ import annotations

from src.data.tx_parser import parse_transaction
from src.wallets.synchronization import detect_synchronized_activity


def _tx(sig: str, mint: str, block_time: int) -> dict:
    return {
        "slot": block_time,
        "blockTime": block_time,
        "meta": {
            "err": None,
            "fee": 5000,
            "preBalances": [100],
            "postBalances": [90],
            "preTokenBalances": [{
                "accountIndex": 0,
                "mint": mint,
                "owner": "owner",
                "uiTokenAmount": {"amount": "0", "decimals": 0},
            }],
            "postTokenBalances": [{
                "accountIndex": 0,
                "mint": mint,
                "owner": "owner",
                "uiTokenAmount": {"amount": "1", "decimals": 0},
            }],
        },
        "transaction": {
            "signatures": [sig],
            "message": {"accountKeys": ["owner"]},
        },
    }


def test_detect_synchronized_activity() -> None:
    a = parse_transaction(_tx("a", "MINT", 100))
    b = parse_transaction(_tx("b", "MINT", 105))
    result = detect_synchronized_activity({"A": [a], "B": [b]}, window_seconds=10)
    assert result[0].matched_events == 1
    assert result[0].synchronization_ratio == 1.0
