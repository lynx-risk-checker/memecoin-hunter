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
