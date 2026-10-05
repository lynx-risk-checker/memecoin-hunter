from __future__ import annotations

from src.data.solana_rpc import SolanaRPCClient, SolanaRPCError


def test_get_signatures_for_address_builds_expected_request() -> None:
    client = SolanaRPCClient("https://example.invalid")
    calls = []

    def fake_call(method, params=None):
        calls.append((method, params))
        return [{"signature": "sig", "slot": 1}]

    client.call = fake_call  # type: ignore[method-assign]
    result = client.get_signatures_for_address("Wallet111", limit=3, before="older")

    assert result[0]["signature"] == "sig"
    assert calls == [
        (
            "getSignaturesForAddress",
            [
                "Wallet111",
                {"limit": 3, "commitment": "confirmed", "before": "older"},
            ],
        )
    ]


def test_get_transaction_uses_json_parsed() -> None:
    client = SolanaRPCClient("https://example.invalid")
    calls = []

    def fake_call(method, params=None):
        calls.append((method, params))
        return {"slot": 123, "meta": None, "transaction": {}}

    client.call = fake_call  # type: ignore[method-assign]
    result = client.get_transaction("signature")

    assert result is not None
    assert result["slot"] == 123
    assert calls == [
        (
            "getTransaction",
            [
                "signature",
                {
                    "commitment": "confirmed",
                    "maxSupportedTransactionVersion": 0,
                    "encoding": "jsonParsed",
                },
            ],
        )
    ]


def test_invalid_history_response_is_rejected() -> None:
    client = SolanaRPCClient("https://example.invalid")

    def fake_call(method, params=None):
        return {"not": "a list"}

    client.call = fake_call  # type: ignore[method-assign]

    try:
        client.get_signatures_for_address("Wallet111")
    except SolanaRPCError:
        pass
    else:
        raise AssertionError("Expected SolanaRPCError")
