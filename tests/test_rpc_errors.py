import json
from unittest.mock import patch

import pytest

from src.data.solana_rpc import SolanaRPCClient, SolanaRPCError


class ErrorResponse:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps({"jsonrpc": "2.0", "id": 1, "error": {"code": -32000}}).encode()


def test_rpc_error_is_not_silently_accepted():
    client = SolanaRPCClient("https://example.invalid")
    with patch("src.data.solana_rpc.urllib.request.urlopen", return_value=ErrorResponse()):
        with pytest.raises(SolanaRPCError):
            client.get_slot()
