from __future__ import annotations

from src.web_snapshot import build_token_forensics


TOKEN = "TargetMint111"
POOL = "PoolAddress111"
WALLET = "WalletAddress111"
SIGNATURE = "ConfirmedSignature111"


class FakeDexClient:
    def token_pairs(self, addresses):
        assert addresses == [TOKEN]
        return [{"pairAddress": POOL}]

    def _best_solana_pair(self, pairs, token):
        assert token == TOKEN
        return pairs[0]


class FakeRPC:
    def __init__(self, transaction):
        self.transaction = transaction
        self.calls = []

    def get_signatures_for_address(self, address, *, limit=10, before=None, until=None, commitment="confirmed"):
        self.calls.append(("getSignaturesForAddress", address, commitment, limit))
        return [{"signature": SIGNATURE, "blockTime": self.transaction["blockTime"], "err": None}]

    def get_transaction(self, signature, *, commitment="confirmed", max_supported_transaction_version=1, encoding="jsonParsed"):
        self.calls.append(("getTransaction", signature, commitment))
        return self.transaction


def transaction(now):
    return {
        "slot": 987,
        "blockTime": now - 30,
        "meta": {
            "err": None,
            "fee": 5000,
            "preBalances": [2_000_000_000, 1_000_000],
            "postBalances": [1_000_000_000, 1_000_000],
            "preTokenBalances": [],
            "postTokenBalances": [{
                "accountIndex": 1,
                "mint": TOKEN,
                "owner": WALLET,
                "uiTokenAmount": {"amount": "2500000", "decimals": 6},
            }],
        },
        "transaction": {
            "signatures": [SIGNATURE],
            "message": {
                "accountKeys": [
                    {"pubkey": WALLET, "signer": True, "writable": True},
                    {"pubkey": "TokenAccount111", "signer": False, "writable": True},
                ],
                "instructions": [],
            },
        },
    }


def test_forensics_endpoint_aggregates_recent_confirmed_balance_flow_as_candidate_only(monkeypatch):
    now = 1_800_000_000
    monkeypatch.delenv("SOLANA_RPC_URL", raising=False)
    rpc = FakeRPC(transaction(now))

    result = build_token_forensics(
        TOKEN,
        client=FakeDexClient(),
        rpc_client=rpc,
        now_epoch=now,
        signature_limit=100,
    )

    assert result["status"] == "CONNECTED"
    assert result["source_method"] == "getSignaturesForAddress + getTransaction"
    assert result["window_seconds"] == 300
    assert result["transactions_parsed"] == 1
    assert result["summary"]["buy_candidates"] == 1
    assert result["summary"]["sell_candidates"] == 0
    assert result["summary"]["unique_buyers_candidate"] == 1
    assert result["summary"]["buy_token_ui"] == 2.5
    assert result["events"][0]["evidence_class"] == "TOKEN_SOL_BALANCE_FLOW_CANDIDATE"
    assert result["events"][0]["dex_swap_confirmed"] is False
    assert result["evidence_status"] == "BALANCE_FLOW_CANDIDATES_ONLY"
    assert result["validation_status"] == "INSUFFICIENT_EVIDENCE"
    assert "getSignaturesForAddress" in [call[0] for call in rpc.calls]
    assert "getTransaction" in [call[0] for call in rpc.calls]


def test_forensics_requires_configured_rpc_when_no_client(monkeypatch):
    monkeypatch.delenv("SOLANA_RPC_URL", raising=False)
    result = build_token_forensics(TOKEN, client=FakeDexClient(), now_epoch=1_800_000_000)
    assert result["status"] == "NOT_CONFIGURED"
    assert result["events"] == []
    assert result["validation_status"] == "INSUFFICIENT_EVIDENCE"


def test_forensics_rejects_invalid_token_without_rpc_calls():
    result = build_token_forensics(" " , client=FakeDexClient(), rpc_client=FakeRPC(transaction(1_800_000_000)))
    assert result["status"] == "INVALID_TOKEN"
