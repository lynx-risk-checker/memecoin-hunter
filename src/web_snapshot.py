from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit
from typing import Any

from src.data.dexscreener import DexScreenerClient, DexScreenerError
from src.radar.token_radar import RadarPolicy, filter_candidates


def _number(value: float | int | None) -> float | None:
    return float(value) if value is not None else None


def build_snapshot(
    client: DexScreenerClient | None = None,
    *,
    max_tokens: int = 10,
    policy: RadarPolicy | None = None,
) -> dict[str, Any]:
    client = client or DexScreenerClient()
    policy = policy or RadarPolicy()
    observed_at = datetime.now(timezone.utc).isoformat()
    try:
        candidates = client.discover(max_tokens=max_tokens)
        candidates = filter_candidates(candidates, policy)
    except (DexScreenerError, ValueError) as exc:
        return {
            "service": "memecoin-hunter",
            "source": "dexscreener",
            "observed_at": observed_at,
            "status": "DATA_UNAVAILABLE",
            "validation_status": "INSUFFICIENT_EVIDENCE",
            "error": str(exc),
            "opportunities": [],
        }

    opportunities: list[dict[str, Any]] = []
    for candidate in candidates:
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
                "decision": "🟡 WATCH",
                "reason": "Radar data received; edge/risk decision requires full evidence pipeline.",
                "liquidity_usd": _number(candidate.liquidity_usd),
                "market_cap_usd": _number(candidate.market_cap_usd),
                "age_seconds": _number(candidate.age_seconds),
                "volume_5m_usd": _number(candidate.volume_5m_usd),
                "volume_1h_usd": _number(candidate.volume_1h_usd),
                "txn_count_5m": candidate.txn_count_5m,
                "txn_count_1h": candidate.txn_count_1h,
                "txns_per_minute": txns_per_minute,
                "smart_money_status": "NOT_EVALUATED",
                "dev_status": "NOT_EVALUATED",
                "cluster_status": "NOT_EVALUATED",
                "exitability": "NOT_EVALUATED",
                "manipulation_status": "NOT_EVALUATED",
                "evidence_status": "RADAR_ONLY",
            }
        )

    return {
        "service": "memecoin-hunter",
        "source": "dexscreener",
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
