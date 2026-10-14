from __future__ import annotations

import base64

from src.web_snapshot import build_token_holders


class FakeRPC:
    def __init__(self):
        self.calls = []

    def call(self, method, params=None):
        self.calls.append((method, params))
        if method == "getTokenLargestAccounts":
            return {"value": [
                {"address": "TokenAccount111", "amount": "4200000", "decimals": 2, "uiAmount": 42000.0}
            ]}
        if method == "getMultipleAccounts":
            raw = bytearray(165)
            raw[0:32] = bytes([9] * 32)
            raw[32:64] = bytes(range(1, 33))
            return {"value": [{"data": [base64.b64encode(raw).decode("ascii"), "base64"]}]}
        raise AssertionError(f"Unexpected RPC method: {method}")


def test_build_token_holders_returns_verified_token_account_authorities():
    rpc = FakeRPC()
    result = build_token_holders("MintAddress111", rpc_client=rpc)

    assert result["status"] == "CONNECTED"
    assert result["holder_count"] == 1
    assert result["holders"][0]["amount"] == 42000.0
    assert result["holders"][0]["token_account"] == "TokenAccount111"
    assert result["holders"][0]["evidence_status"] == "CONFIRMED_EVIDENCE"
    assert result["nodes"][0]["kind"] == "mint"
    assert result["nodes"][1]["kind"] == "token-account-authority"
    assert result["edges"][0]["kind"] == "TOKEN_ACCOUNT_AUTHORITY"
    assert [method for method, _ in rpc.calls] == [
        "getTokenLargestAccounts",
        "getMultipleAccounts",
    ]


def test_build_token_holders_rejects_empty_token_without_rpc_call():
    rpc = FakeRPC()
    result = build_token_holders("", rpc_client=rpc)

    assert result["status"] == "INVALID_TOKEN"
    assert result["holders"] == []
    assert rpc.calls == []


def test_base58_encoding_preserves_leading_zero_bytes():
    from src.web_snapshot import _base58_encode

    assert _base58_encode(bytes(32)) == "1" * 32
    assert _base58_encode(bytes([0, 1])) == "12"
