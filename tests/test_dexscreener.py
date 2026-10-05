from unittest.mock import patch

from src.data.dexscreener import DexScreenerClient


def test_discover_maps_solana_profile_and_pair():
    client = DexScreenerClient("https://example.invalid")
    profiles = [
        {"chainId": "solana", "tokenAddress": "TOKEN1"},
        {"chainId": "ethereum", "tokenAddress": "OTHER"},
    ]
    pairs = [
        {
            "chainId": "solana",
            "baseToken": {"address": "TOKEN1", "name": "Example", "symbol": "EX"},
            "pairCreatedAt": 1_700_000_000_000,
            "liquidity": {"usd": 1234.5},
            "marketCap": 9876.5,
        }
    ]

    with patch.object(DexScreenerClient, "latest_profiles", return_value=profiles):
        with patch.object(DexScreenerClient, "token_pairs", return_value=pairs):
            result = client.discover()

    assert len(result) == 1
    assert result[0].address == "TOKEN1"
    assert result[0].source == "dexscreener"
    assert result[0].liquidity_usd == 1234.5
    assert result[0].market_cap_usd == 9876.5
    assert result[0].age_seconds is not None


def test_get_sends_json_accept_and_user_agent_headers():
    client = DexScreenerClient("https://example.invalid")
    response = object()

    with patch("src.data.dexscreener.urllib.request.urlopen") as urlopen:
        context = urlopen.return_value.__enter__.return_value
        context.read.return_value = b"[]"
        with patch("src.data.dexscreener.urllib.request.Request") as request:
            client._get("/test")
            request.assert_called_once()
            kwargs = request.call_args.kwargs
            assert kwargs["headers"]["Accept"] == "application/json"
            assert kwargs["headers"]["User-Agent"] == "memecoin-hunter/0.1 (+read-only)"
        assert response is not None
