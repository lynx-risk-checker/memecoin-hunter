from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from typing import Any

from src.data.dexscreener import DexScreenerClient, DexScreenerError
from src.data.solana_rpc import SolanaRPCClient, SolanaRPCError
from src.wallets.history import collect_wallet_transactions
from src.wallets.swap_evidence import extract_balance_flow_swaps
from src.radar.token_radar import RadarPolicy, filter_candidates


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
        candidates = client.discover(max_tokens=max_tokens)
        candidates = filter_candidates(candidates, policy)
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
    for candidate in candidates:
        observed_swaps = []
        if wallet_collection_status == "COLLECTED":
            for wallet, transactions in wallet_transactions.items():
                observed_swaps.extend(
                    extract_balance_flow_swaps(
                        wallet, transactions, target_mint=candidate.address, quote_mint="SOL"
                    )
                )
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
                "reason": "Market radar only. Wallet/on-chain flow, expected value, and security evidence are not yet evaluated; entry remains blocked.",
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
                "tracked_wallet_buyers": len({swap_wallet for swap_wallet in wallet_transactions if any(swap.signature == tx.signature and swap.direction == "BUY" for tx in onchain_buys for swap in extract_balance_flow_swaps(swap_wallet, wallet_transactions[swap_wallet], target_mint=candidate.address, quote_mint="SOL"))}) if wallet_collection_status == "COLLECTED" else None,
                "tracked_wallet_sellers": len({swap_wallet for swap_wallet in wallet_transactions if any(swap.signature == tx.signature and swap.direction == "SELL" for tx in onchain_sells for swap in extract_balance_flow_swaps(swap_wallet, wallet_transactions[swap_wallet], target_mint=candidate.address, quote_mint="SOL"))}) if wallet_collection_status == "COLLECTED" else None,
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
        "opportunities": opportunities,
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
        if path == "/snapshot":
            self._write_json(200, build_snapshot(self.client))
            return
        if self._serve_static(path):
            return
        self._write_json(404, {"status": "NOT_FOUND"})

    def log_message(self, format: str, *args: object) -> None:
        return


def serve(host: str | None = None, port: int | None = None) -> None:
    host = host or os.getenv("SNAPSHOT_HOST", "0.0.0.0")
    port = port or int(os.getenv("PORT", os.getenv("SNAPSHOT_PORT", "8080")) )
    server = ThreadingHTTPServer((host, port), SnapshotHandler)
    server.serve_forever()


if __name__ == "__main__":
    serve()
