from __future__ import annotations

import io
import json
import urllib.error

import pytest

import src.data.solana_rpc as solana_rpc
import src.web_snapshot as web_snapshot
from src.data.solana_rpc import SolanaRPCClient, SolanaRPCError


TOKEN = "TargetMint111"
POOL = "VerifiedPool111"


class FakeDexClient:
    def token_pairs(self, addresses):
        assert addresses == [TOKEN]
        return [{"pairAddress": POOL}]

    def _best_solana_pair(self, pairs, token):
        assert token == TOKEN
        return pairs[0]


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return self.payload


def test_candles_explain_when_geckoterminal_has_no_indexed_rows(monkeypatch):
    monkeypatch.setattr(
        web_snapshot.urllib.request,
        "urlopen",
        lambda *args, **kwargs: FakeResponse({"data": {"attributes": {"ohlcv_list": []}}}),
    )

    result = web_snapshot.build_candles(FakeDexClient(), TOKEN, "day")

    assert result["status"] == "NO_CANDLES"
    assert result["candles"] == []
    assert "no OHLCV rows yet" in result["error"]


def test_candles_expose_upstream_http_status_without_fabricating_data(monkeypatch):
    def fail(*args, **kwargs):
        raise urllib.error.HTTPError(
            "https://api.geckoterminal.com/api/v2/pools/test",
            429,
            "Too Many Requests",
            {},
            io.BytesIO(b'{"errors":[{"detail":"rate limit"}]}'),
        )

    monkeypatch.setattr(web_snapshot.urllib.request, "urlopen", fail)

    result = web_snapshot.build_candles(FakeDexClient(), TOKEN, "minute")

    assert result["status"] == "UNAVAILABLE"
    assert result["candles"] == []
    assert "HTTP 429" in result["error"]
    assert "rate limit" in result["error"]


def test_solana_rpc_reports_http_status_for_the_failed_method(monkeypatch):
    def fail(*args, **kwargs):
        raise urllib.error.HTTPError("https://rpc.invalid/secret", 429, "Too Many Requests", {}, io.BytesIO(b""))

    monkeypatch.setattr(solana_rpc.urllib.request, "urlopen", fail)

    with pytest.raises(SolanaRPCError, match="HTTP 429 for getTokenLargestAccounts") as error:
        SolanaRPCClient("https://rpc.invalid/secret").call("getTokenLargestAccounts", [TOKEN])

    assert "secret" not in str(error.value)


def test_solana_rpc_reports_timeout_without_exposing_endpoint(monkeypatch):
    def fail(*args, **kwargs):
        raise urllib.error.URLError(TimeoutError("timed out"))

    monkeypatch.setattr(solana_rpc.urllib.request, "urlopen", fail)

    with pytest.raises(SolanaRPCError, match="getSignaturesForAddress.*timeout") as error:
        SolanaRPCClient("https://rpc.invalid/secret").call("getSignaturesForAddress", [POOL, {}])

    assert "secret" not in str(error.value)



def test_dashboard_response_cache_reuses_provider_result(monkeypatch):
    handler = web_snapshot.SnapshotHandler
    with handler._response_cache_lock:
        handler._response_cache.clear()
        handler._response_key_locks.clear()
    clock = {"now": 100.0}
    monkeypatch.setattr(web_snapshot.time, "monotonic", lambda: clock["now"])
    calls = []

    def build():
        calls.append("called")
        return {"status": "UNAVAILABLE", "error": "HTTP 429"}

    first = handler._cached_response("test:429", 30.0, build)
    second = handler._cached_response("test:429", 30.0, build)

    assert first == second == {"status": "UNAVAILABLE", "error": "HTTP 429"}
    assert calls == ["called"]


def test_dashboard_response_cache_refreshes_after_ttl(monkeypatch):
    handler = web_snapshot.SnapshotHandler
    with handler._response_cache_lock:
        handler._response_cache.clear()
        handler._response_key_locks.clear()
    clock = {"now": 100.0}
    monkeypatch.setattr(web_snapshot.time, "monotonic", lambda: clock["now"])
    calls = []

    def build():
        calls.append(len(calls) + 1)
        return {"sequence": calls[-1]}

    assert handler._cached_response("test:ttl", 5.0, build) == {"sequence": 1}
    clock["now"] = 106.0
    assert handler._cached_response("test:ttl", 5.0, build) == {"sequence": 2}
    assert calls == [1, 2]
