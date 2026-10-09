from unittest.mock import patch

from src.data.dexscreener import DexScreenerClient, DexScreenerError


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
            "txns": {"m5": {"buys": 17, "sells": 8}, "h1": {"buys": 90, "sells": 40}},
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
    assert result[0].buy_txns_5m == 17
    assert result[0].sell_txns_5m == 8
    assert result[0].buy_txns_1h == 90
    assert result[0].sell_txns_1h == 40
    assert result[0].txn_count_5m == 25
    assert result[0].age_seconds is not None


def test_get_sends_json_accept_and_user_agent_headers():
    client = DexScreenerClient("https://example.invalid")
    with patch("src.data.dexscreener.urllib.request.urlopen") as urlopen:
        context = urlopen.return_value.__enter__.return_value
        context.read.return_value = b"[]"
        with patch("src.data.dexscreener.urllib.request.Request") as request:
            client._get("/test")
            kwargs = request.call_args.kwargs
            assert kwargs["headers"]["Accept"] == "application/json"
            assert kwargs["headers"]["User-Agent"] == "memecoin-hunter/0.1 (+read-only)"


def test_snapshot_maps_realistic_pair_fields():
    client = DexScreenerClient("https://example.invalid")
    pairs = [
        {
            "chainId": "solana",
            "baseToken": {"address": "TOKEN1", "name": "Example", "symbol": "EX"},
            "priceUsd": "1.25",
            "liquidity": {"usd": 5000.0},
            "volume": {"h24": 25000.0},
            "txns": {"h24": {"buys": 120, "sells": 80}},
            "marketCap": 100000.0,
        }
    ]
    with patch.object(DexScreenerClient, "token_pairs", return_value=pairs):
        result = client.snapshot("TOKEN1")

    assert result.price_usd == 1.25
    assert result.liquidity_usd == 5000.0
    assert result.volume_usd == 25000.0
    assert result.buy_count == 120
    assert result.sell_count == 80
    assert result.unique_buyers is None
    assert result.holder_count is None


def test_snapshot_rejects_incomplete_pair():
    client = DexScreenerClient("https://example.invalid")
    with patch.object(DexScreenerClient, "token_pairs", return_value=[{"chainId": "solana"}]):
        try:
            client.snapshot("TOKEN1")
        except DexScreenerError as exc:
            assert "Snapshot incomplete" in str(exc)
        else:
            raise AssertionError("Expected DexScreenerError")


def test_discover_prefers_highest_liquidity_solana_pair():
    client = DexScreenerClient("https://example.invalid")
    profiles = [{"chainId": "solana", "tokenAddress": "TOKEN1"}]
    pairs = [
        {"chainId": "solana", "baseToken": {"address": "TOKEN1"}, "liquidity": {"usd": 10}},
        {"chainId": "solana", "baseToken": {"address": "TOKEN1"}, "liquidity": {"usd": 100}},
    ]
    with patch.object(DexScreenerClient, "latest_profiles", return_value=profiles):
        with patch.object(DexScreenerClient, "token_pairs", return_value=pairs):
            result = client.discover()
    assert result[0].liquidity_usd == 100.0
