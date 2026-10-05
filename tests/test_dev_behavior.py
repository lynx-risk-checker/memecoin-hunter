from __future__ import annotations

from src.data.tx_parser import parse_transaction
from src.dev.behavior import assess_dev_behavior


def test_assess_dev_behavior_uses_explicit_token_owner_deltas() -> None:
    tx = {
        "slot": 1,
        "blockTime": 1,
        "meta": {
            "err": None,
            "fee": 5000,
            "preBalances": [100],
            "postBalances": [90],
            "preTokenBalances": [{
                "accountIndex": 0,
                "mint": "M",
                "owner": "DEV",
                "uiTokenAmount": {"amount": "10", "decimals": 0},
            }],
            "postTokenBalances": [{
                "accountIndex": 0,
                "mint": "M",
                "owner": "DEV",
                "uiTokenAmount": {"amount": "5", "decimals": 0},
            }],
        },
        "transaction": {
            "signatures": ["s"],
            "message": {"accountKeys": ["DEV"]},
        },
    }
    result = assess_dev_behavior("DEV", [parse_transaction(tx)])
    assert result.token_outflows == 1
    assert result.status == "OUTFLOW_HEAVY"
