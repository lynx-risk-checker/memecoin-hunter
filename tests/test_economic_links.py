from __future__ import annotations

from src.data.tx_parser import parse_transaction
from src.wallets.economic_links import detect_link_evidence


def _tx(sig: str, mint: str) -> dict:
    return {
        "slot": 1,
        "blockTime": 1,
        "meta": {
            "err": None, "fee": 5000,
            "preBalances": [100, 100], "postBalances": [90, 110],
            "preTokenBalances": [{"accountIndex": 1, "mint": mint, "owner": "owner", "uiTokenAmount": {"amount": "0", "decimals": 0}}],
            "postTokenBalances": [{"accountIndex": 1, "mint": mint, "owner": "owner", "uiTokenAmount": {"amount": "1", "decimals": 0}}],
        },
        "transaction": {"signatures": [sig], "message": {"accountKeys": ["a", "b"]}},
    }


def test_detect_link_evidence_combines_token_and_transaction_history() -> None:
    a = parse_transaction(_tx("same", "M1"))
    b = parse_transaction(_tx("same", "M1"))
    links = detect_link_evidence({"A": [a], "B": [b]}, min_shared_tokens=1)
    assert len(links) == 1
    assert links[0].shared_tokens == 1
    assert links[0].shared_transactions == 1
