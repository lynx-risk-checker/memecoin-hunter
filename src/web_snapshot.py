from __future__ import annotations

import asyncio
import base64
import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit
import urllib.error
import urllib.request
from typing import Any

from src.data.dexscreener import DexScreenerClient, DexScreenerError
from src.data.solana_rpc import SolanaRPCClient, SolanaRPCError
from src.data.solana_stream import SolanaLogStream
from src.wallets.history import collect_wallet_transactions
from src.wallets.swap_evidence import extract_balance_flow_swaps
from src.radar.token_radar import RadarPolicy, candidate_filter_reasons, filter_candidates


def _number(value: float | int | None) -> float | None:
    return float(value) if value is not None else None


def build_snapshot(
    client: DexScreenerClient | None = None,
    *,
    max_tokens: int = 10,
    policy: RadarPolicy | None = None,
    rpc_client: SolanaRPCClient | None = None,
) -> dict[str, Any]:
    client = client or DexScreenerClient()
    policy = policy or RadarPolicy()
    observed_at = datetime.now(timezone.utc).isoformat()
    rpc_url = os.getenv("SOLANA_RPC_URL", "").strip()
    rpc_status: dict[str, Any] = {"status": "NOT_CONFIGURED"}
    rpc: Any = rpc_client
    if rpc_client is not None:
        try:
            rpc_status = {"status": "CONNECTED", "health": rpc_client.get_health(), "slot": rpc_client.get_slot()}
        except (SolanaRPCError, ValueError, OSError) as exc:
            rpc_status = {"status": "UNAVAILABLE", "error": str(exc)}
    elif rpc_url:
        try:
            rpc = SolanaRPCClient(rpc_url, timeout_seconds=2.5)
            rpc_status = {"status": "CONNECTED", "health": rpc.get_health(), "slot": rpc.get_slot()}
        except (SolanaRPCError, ValueError, OSError) as exc:
            rpc_status = {"status": "UNAVAILABLE", "error": str(exc)}
    try:
        discovered_candidates = client.discover(max_tokens=max_tokens)
        candidates = filter_candidates(discovered_candidates, policy)
        # Keep genuine discovered market candidates visible when the strict
        # early-radar policy rejects every candidate. They remain WAIT-only and
        # are explicitly marked as filtered; never manufacture placeholder data.
        display_candidates = candidates if candidates else discovered_candidates[:max_tokens]
        eligible_addresses = {candidate.address for candidate in candidates}
    except (DexScreenerError, ValueError) as exc:
        return {
            "service": "memecoin-hunter",
            "source": "dexscreener",
            "sources": {"dexscreener": {"status": "UNAVAILABLE"}, "solana_rpc": rpc_status},
            "observed_at": observed_at,
            "status": "DATA_UNAVAILABLE",
            "validation_status": "INSUFFICIENT_EVIDENCE",
            "error": str(exc),
            "opportunities": [],
        }

    watched_wallets = list(dict.fromkeys(
        wallet.strip()
        for wallet in os.getenv("WATCHED_WALLET_ADDRESSES", "").split(",")
        if wallet.strip()
    ))[:10]
    wallet_transactions: dict[str, tuple[Any, ...]] = {}
    wallet_collection_status = "NOT_CONFIGURED" if not watched_wallets else "UNAVAILABLE"
    if watched_wallets and rpc is not None and rpc_status.get("status") == "CONNECTED":
        try:
            for wallet in watched_wallets:
                wallet_transactions[wallet] = tuple(
                    item.transaction for item in collect_wallet_transactions(rpc, wallet, limit=5)
                )
            wallet_collection_status = "COLLECTED"
        except (SolanaRPCError, ValueError, OSError) as exc:
            wallet_collection_status = "UNAVAILABLE"
            rpc_status = {**rpc_status, "wallet_collection_error": str(exc)}

    opportunities: list[dict[str, Any]] = []
    for candidate in display_candidates:
        radar_eligible = candidate.address in eligible_addresses
        observed_swaps = []
        wallets_by_direction: dict[str, set[str]] = {"BUY": set(), "SELL": set()}
        if wallet_collection_status == "COLLECTED":
            for wallet, transactions in wallet_transactions.items():
                wallet_swaps = extract_balance_flow_swaps(
                    wallet, transactions, target_mint=candidate.address, quote_mint="SOL"
                )
                observed_swaps.extend(wallet_swaps)
                for swap in wallet_swaps:
                    wallets_by_direction[swap.direction].add(wallet)
        onchain_buys = [swap for swap in observed_swaps if swap.direction == "BUY"]
        onchain_sells = [swap for swap in observed_swaps if swap.direction == "SELL"]

        txns_per_minute = (
            candidate.txn_count_5m / 5.0
            if candidate.txn_count_5m is not None
            else None
        )
        opportunities.append(
            {
                "token": candidate.address,
                "symbol": candidate.symbol,
                "name": candidate.name,
                "decision": "WAIT",
                "reason": (
                    "Market radar only. Wallet/on-chain flow, expected value, and security evidence are not yet evaluated; entry remains blocked."
                    if radar_eligible else
                    "Real DEX candidate shown for visibility, but it did not pass the current radar policy. Entry remains blocked."
                ),
                "radar_eligibility": "QUALIFIES_FOR_RADAR" if radar_eligible else "FILTERED_BY_RADAR_POLICY",
                "radar_filter_reasons": [] if radar_eligible else candidate_filter_reasons(candidate, policy),
                "liquidity_usd": _number(candidate.liquidity_usd),
                "market_cap_usd": _number(candidate.market_cap_usd),
                "age_seconds": _number(candidate.age_seconds),
                "volume_5m_usd": _number(candidate.volume_5m_usd),
                "volume_1h_usd": _number(candidate.volume_1h_usd),
                "txn_count_5m": candidate.txn_count_5m,
                "txn_count_1h": candidate.txn_count_1h,
                "buy_txns_5m": candidate.buy_txns_5m,
                "sell_txns_5m": candidate.sell_txns_5m,
                "buy_txns_1h": candidate.buy_txns_1h,
                "sell_txns_1h": candidate.sell_txns_1h,
                "txns_per_minute": txns_per_minute,
                "smart_money_status": "NOT_EVALUATED",
                "dev_status": "NOT_EVALUATED",
                "cluster_status": "NOT_EVALUATED",
                "exitability": "NOT_EVALUATED",
                "manipulation_status": "NOT_EVALUATED",
                "evidence_status": "ONCHAIN_WALLET_FLOW_OBSERVED" if observed_swaps else "MARKET_ACTIVITY_ONLY",
                "onchain_flow_status": wallet_collection_status,
                "onchain_buy_txns": len(onchain_buys) if wallet_collection_status == "COLLECTED" else None,
                "onchain_sell_txns": len(onchain_sells) if wallet_collection_status == "COLLECTED" else None,
                "tracked_wallet_buyers": len(wallets_by_direction["BUY"]) if wallet_collection_status == "COLLECTED" else None,
                "tracked_wallet_sellers": len(wallets_by_direction["SELL"]) if wallet_collection_status == "COLLECTED" else None,
                "onchain_signatures": list(dict.fromkeys(swap.signature for swap in observed_swaps if swap.signature))[:5],
            }
        )

    return {
        "service": "memecoin-hunter",
        "source": "dexscreener",
        "sources": {"dexscreener": {"status": "CONNECTED"}, "solana_rpc": rpc_status, "watched_wallets": {"status": wallet_collection_status, "configured_count": len(watched_wallets), "collected_count": len(wallet_transactions)}},
        "observed_at": observed_at,
        "status": "READY",
        "mode": "PAPER / DRY RUN",
        "execution": "LOCKED",
        "validation_status": "INSUFFICIENT_EVIDENCE",
        "discovery": {
            "discovered_candidate_count": len(discovered_candidates),
            "qualifying_candidate_count": len(candidates),
            "displayed_candidate_count": len(opportunities),
            "display_mode": "QUALIFIED" if candidates else ("FILTERED_FALLBACK" if discovered_candidates else "EMPTY"),
        },
        "opportunities": opportunities,
    }


def build_candles(client: DexScreenerClient, token_address: str, timeframe: str = "minute") -> dict[str, Any]:
    """Fetch real OHLCV candles from GeckoTerminal for a verified DexScreener Solana pool."""
    intervals = {"minute": ("minute", "1"), "5m": ("minute", "5"), "hour": ("hour", "1"), "day": ("day", "1")}
    if timeframe not in intervals:
        return {"status": "INVALID_TIMEFRAME", "source": "geckoterminal", "candles": []}
    if not token_address or len(token_address) > 64:
        return {"status": "INVALID_TOKEN", "source": "geckoterminal", "candles": []}
    try:
        pairs = client.token_pairs([token_address])
        pair = client._best_solana_pair(pairs, token_address)
        if not pair or not isinstance(pair.get("pairAddress"), str):
            return {"status": "POOL_NOT_FOUND", "source": "geckoterminal", "token": token_address, "candles": []}
        candle_interval, aggregate = intervals[timeframe]
        query = urlencode({"aggregate": aggregate, "limit": "120", "currency": "usd", "token": "base"})
        url = f"https://api.geckoterminal.com/api/v2/networks/solana/pools/{pair['pairAddress']}/ohlcv/{candle_interval}?{query}"
        request = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "memecoin-hunter/0.1 (+read-only)"}, method="GET")
        with urllib.request.urlopen(request, timeout=8.0) as response:
            body = json.loads(response.read().decode("utf-8"))
        attributes = body.get("data", {}).get("attributes", {}) if isinstance(body, dict) else {}
        raw_rows = attributes.get("ohlcv_list", []) if isinstance(attributes, dict) else []
        candles = []
        for row in raw_rows if isinstance(raw_rows, list) else []:
            if not isinstance(row, list) or len(row) < 6:
                continue
            try:
                timestamp, open_price, high, low, close, volume = row[:6]
                values = [float(open_price), float(high), float(low), float(close), float(volume)]
                if not all(__import__("math").isfinite(value) for value in values):
                    continue
                candles.append({"time": int(timestamp), "open": values[0], "high": values[1], "low": values[2], "close": values[3], "volume": max(0.0, values[4])})
            except (TypeError, ValueError, OverflowError):
                continue
        candles.sort(key=lambda item: item["time"])
        return {"status": "CONNECTED" if candles else "NO_CANDLES", "source": "geckoterminal", "token": token_address, "pair_address": pair["pairAddress"], "timeframe": timeframe, "observed_at": datetime.now(timezone.utc).isoformat(), "candles": candles}
    except (DexScreenerError, urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError, OSError):
        return {"status": "UNAVAILABLE", "source": "geckoterminal", "token": token_address, "timeframe": timeframe, "candles": []}


def _base58_encode(raw: bytes) -> str:
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    number = int.from_bytes(raw, "big")
    encoded = ""
    while number:
        number, remainder = divmod(number, 58)
        encoded = alphabet[remainder] + encoded
    zeroes = len(raw) - len(raw.lstrip(b"\\x00"))
    return "1" * zeroes + (encoded or ("" if zeroes else "1"))


def build_token_holders(token_address: str, rpc_client: SolanaRPCClient | None = None) -> dict[str, Any]:
    """Fetch real largest token accounts and decode their on-chain token authorities."""
    token = token_address.strip()
    observed_at = datetime.now(timezone.utc).isoformat()
    if not token or len(token) > 64:
        return {"status": "INVALID_TOKEN", "source": "solana-rpc", "token": token, "holders": [], "nodes": [], "edges": []}
    rpc_url = os.getenv("SOLANA_RPC_URL", "").strip() or "https://api.mainnet-beta.solana.com"
    rpc = rpc_client or SolanaRPCClient(rpc_url, timeout_seconds=5.0)
    try:
        largest = rpc.call("getTokenLargestAccounts", [token, {"commitment": "confirmed"}])
        rows = largest.get("value", []) if isinstance(largest, dict) else []
        rows = [row for row in rows if isinstance(row, dict) and isinstance(row.get("address"), str)]
        rows = rows[:10]
        if not rows:
            return {"status": "NO_HOLDERS", "source": "solana-rpc", "token": token, "observed_at": observed_at, "holders": [], "nodes": [], "edges": []}
        accounts = rpc.call("getMultipleAccounts", [[row["address"] for row in rows], {"encoding": "base64", "commitment": "confirmed"}])
        values = accounts.get("value", []) if isinstance(accounts, dict) else []
        holders = []
        seen_owners: set[str] = set()
        for row, account in zip(rows, values):
            if not isinstance(account, dict):
                continue
            data = account.get("data")
            if not isinstance(data, list) or not data or not isinstance(data[0], str):
                continue
            try:
                raw = base64.b64decode(data[0], validate=True)
            except (ValueError, TypeError):
                continue
            # SPL Token account layout: mint[0:32], authority/owner[32:64].
            if len(raw) < 64:
                continue
            owner = _base58_encode(raw[32:64])
            if not owner or owner in seen_owners:
                continue
            seen_owners.add(owner)
            amount = row.get("uiAmount")
            if not isinstance(amount, (int, float)):
                try:
                    amount = float(row.get("amount", "0")) / (10 ** int(row.get("decimals", 0)))
                except (TypeError, ValueError, OverflowError):
                    amount = None
            holders.append({
                "rank": len(holders) + 1,
                "wallet": owner,
                "token_account": row["address"],
                "amount": amount,
                "raw_amount": row.get("amount"),
                "decimals": row.get("decimals"),
                "source": "getTokenLargestAccounts + getMultipleAccounts",
                "evidence_status": "CONFIRMED_EVIDENCE",
            })
        nodes = [{"id": "mint:" + token, "address": token, "label": "TOKEN MINT", "kind": "mint", "evidence_status": "CONFIRMED_EVIDENCE"}]
        edges = []
        for holder in holders:
            nodes.append({"id": holder["wallet"], "address": holder["wallet"], "label": "HOLDER #" + str(holder["rank"]), "kind": "token-account-authority", "amount": holder["amount"], "evidence_status": "CONFIRMED_EVIDENCE"})
            edges.append({"source": "mint:" + token, "target": holder["wallet"], "kind": "TOKEN_ACCOUNT_AUTHORITY", "evidence_status": "CONFIRMED_EVIDENCE"})
        return {
            "status": "CONNECTED" if holders else "INSUFFICIENT_EVIDENCE",
            "source": "solana-rpc",
            "rpc_endpoint_kind": "configured" if os.getenv("SOLANA_RPC_URL", "").strip() else "public-fallback",
            "token": token,
            "observed_at": observed_at,
            "holder_count": len(holders),
            "holders": holders,
            "nodes": nodes,
            "edges": edges,
            "note": "Authorities of the largest token accounts; these are not wallet-to-wallet transfer edges and may include pool/program authorities.",
        }
    except (SolanaRPCError, ValueError, OSError, TypeError, KeyError) as exc:
        return {
            "status": "UNAVAILABLE",
            "source": "solana-rpc",
            "token": token,
            "observed_at": observed_at,
            "error": str(exc),
            "holders": [],
            "nodes": [],
            "edges": [],
        }


WEB_ROOT = Path(__file__).resolve().parent.parent / "web"
STATIC_FILES = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/index.html": ("index.html", "text/html; charset=utf-8"),
    "/app.js": ("app.js", "application/javascript; charset=utf-8"),
    "/styles.css": ("styles.css", "text/css; charset=utf-8"),
    "/manifest.webmanifest": ("manifest.webmanifest", "application/manifest+json; charset=utf-8"),
    "/icons/icon.svg": ("icons/icon.svg", "image/svg+xml"),
    "/sw.js": ("sw.js", "application/javascript; charset=utf-8"),
}


class SnapshotHandler(BaseHTTPRequestHandler):
    client = DexScreenerClient()

    def _write_bytes(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _write_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        self._write_bytes(status, body, "application/json; charset=utf-8")

    def _serve_static(self, path: str) -> bool:
        target = STATIC_FILES.get(path)
        if target is None:
            return False
        filename, content_type = target
        try:
            body = (WEB_ROOT / filename).read_bytes()
        except FileNotFoundError:
            self._write_json(404, {"status": "NOT_FOUND"})
            return True
        self._write_bytes(200, body, content_type)
        return True

    def do_GET(self) -> None:  # noqa: N802
        path = urlsplit(self.path).path
        if path == "/stream":
            query = parse_qs(urlsplit(self.path).query)
            token = query.get("token", [""])[0].strip()
            if not token or len(token) > 64:
                self._write_json(400, {"status": "INVALID_TOKEN", "source": "solana-logsSubscribe"})
                return
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-transform")
            self.send_header("Connection", "keep-alive")
            self.send_header("X-Accel-Buffering", "no")
            self.end_headers()
            try:
                asyncio.run(self._serve_token_stream(token))
            except (BrokenPipeError, ConnectionResetError):
                return
            except Exception as exc:
                try:
                    payload = json.dumps({"status": "UNAVAILABLE", "source": "solana-logsSubscribe", "error": str(exc)}, separators=(",", ":")).encode("utf-8")
                    self.wfile.write(b"event: status\\ndata: " + payload + b"\\n\\n")
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError, OSError):
                    pass
            return
        if path == "/snapshot":
            self._write_json(200, build_snapshot(self.client))
            return
        if path == "/candles":
            query = parse_qs(urlsplit(self.path).query)
            token = query.get("token", [""])[0].strip()
            timeframe = query.get("timeframe", ["minute"])[0].strip()
            self._write_json(200, build_candles(self.client, token, timeframe))
            return
        if path == "/holders":
            query = parse_qs(urlsplit(self.path).query)
            token = query.get("token", [""])[0].strip()
            self._write_json(200, build_token_holders(token))
            return
        if self._serve_static(path):
            return
        self._write_json(404, {"status": "NOT_FOUND"})


    async def _serve_token_stream(self, token: str) -> None:
        endpoint = (
            os.getenv("SOLANA_WS_URL", "").strip()
            or os.getenv("SOLANA_RPC_URL", "").strip()
            or "https://api.mainnet-beta.solana.com"
        )
        stream = SolanaLogStream(endpoint, commitment="confirmed", reconnect_delay=2.0)
        self.wfile.write(b'event: status\\ndata: {"status":"CONNECTING","source":"solana-logsSubscribe"}\\n\\n')
        self.wfile.flush()
        async for item in stream.events(mentions=token):
            payload = json.dumps({
                "status": "TOKEN_LOG_EVENT",
                "source": "solana-logsSubscribe",
                "token": token,
                "slot": item.slot,
                "signature": item.signature,
                "err": item.err,
                "logs": list(item.logs[:8]),
                "observed_at": datetime.now(timezone.utc).isoformat(),
            }, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
            self.wfile.write(b"event: tx\\ndata: " + payload + b"\\n\\n")
            self.wfile.flush()

    def log_message(self, format: str, *args: object) -> None:
        return


def serve(host: str | None = None, port: int | None = None) -> None:
    host = host or os.getenv("SNAPSHOT_HOST", "0.0.0.0")
    port = port or int(os.getenv("PORT", os.getenv("SNAPSHOT_PORT", "8080")) )
    server = ThreadingHTTPServer((host, port), SnapshotHandler)
    server.serve_forever()


if __name__ == "__main__":
    serve()
