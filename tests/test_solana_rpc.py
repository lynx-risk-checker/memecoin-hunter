import json
from unittest.mock import patch

from src.data.solana_rpc import SolanaRPCClient


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps({"jsonrpc": "2.0", "id": 1, "result": 123}).encode()


def test_get_slot_uses_json_rpc():
    client = SolanaRPCClient("https://example.invalid")
    with patch("src.data.solana_rpc.urllib.request.urlopen", return_value=FakeResponse()):
        assert client.get_slot() == 123



def test_rpc_retries_rate_limit_then_succeeds():
    from urllib.error import HTTPError
    from io import BytesIO

    client = SolanaRPCClient("https://example.invalid", max_attempts=2)
    rate_limited = HTTPError(
        "https://example.invalid", 429, "Too Many Requests",
        {"Retry-After": "0"}, BytesIO(b""),
    )
    with patch("src.data.solana_rpc.urllib.request.urlopen", side_effect=[rate_limited, FakeResponse()]) as open_url, patch("src.data.solana_rpc.time.sleep") as sleep:
        assert client.get_slot() == 123
    assert open_url.call_count == 2
    sleep.assert_called_once_with(0.0)


def test_rpc_does_not_retry_forbidden_response():
    from urllib.error import HTTPError
    from io import BytesIO
    from src.data.solana_rpc import SolanaRPCError

    client = SolanaRPCClient("https://example.invalid", max_attempts=3)
    forbidden = HTTPError(
        "https://example.invalid", 403, "Forbidden", {}, BytesIO(b""),
    )
    with patch("src.data.solana_rpc.urllib.request.urlopen", side_effect=forbidden) as open_url:
        try:
            client.get_slot()
        except SolanaRPCError as exc:
            assert "HTTP 403" in str(exc)
        else:
            raise AssertionError("HTTP 403 should fail closed")
    assert open_url.call_count == 1
