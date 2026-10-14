from __future__ import annotations

import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

import src.web_snapshot as web_snapshot


def _request(server: ThreadingHTTPServer, path: str):
    url = f"http://127.0.0.1:{server.server_port}{path}"
    with urllib.request.urlopen(url, timeout=2) as response:
        return response.status, response.headers.get("Content-Type", ""), response.read()


def test_snapshot_route_accepts_query_string(monkeypatch):
    payload = {
        "service": "memecoin-hunter",
        "status": "READY",
        "sources": {
            "dexscreener": {"status": "CONNECTED"},
            "solana_rpc": {"status": "NOT_CONFIGURED"},
        },
        "execution": "LOCKED",
        "validation_status": "INSUFFICIENT_EVIDENCE",
        "opportunities": [],
    }
    monkeypatch.setattr(web_snapshot, "build_snapshot", lambda client: payload)
    server = ThreadingHTTPServer(("127.0.0.1", 0), web_snapshot.SnapshotHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, content_type, body = _request(server, "/snapshot?ui=16&t=123")
        assert status == 200
        assert content_type.startswith("application/json")
        result = json.loads(body)
        assert result["sources"]["solana_rpc"]["status"] == "NOT_CONFIGURED"
        assert result["execution"] == "LOCKED"
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()


def test_static_asset_route_accepts_query_string():
    server = ThreadingHTTPServer(("127.0.0.1", 0), web_snapshot.SnapshotHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, content_type, body = _request(server, "/app.js?ui=16&t=123")
        assert status == 200
        assert content_type.startswith("application/javascript")
        assert body
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()


def test_forensics_route_passes_selected_token_and_returns_evidence(monkeypatch):
    observed = []
    payload = {
        "status": "CONNECTED",
        "source": "solana-rpc",
        "token": "Mint111",
        "window_seconds": 300,
        "evidence_status": "BALANCE_FLOW_CANDIDATES_ONLY",
        "events": [],
    }

    def fake_forensics(token, *, client=None):
        observed.append(token)
        return payload

    monkeypatch.setattr(web_snapshot, "build_token_forensics", fake_forensics)
    server = ThreadingHTTPServer(("127.0.0.1", 0), web_snapshot.SnapshotHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        status, content_type, body = _request(server, "/forensics?token=Mint111&t=123")
        assert status == 200
        assert content_type.startswith("application/json")
        result = json.loads(body)
        assert result["window_seconds"] == 300
        assert result["evidence_status"] == "BALANCE_FLOW_CANDIDATES_ONLY"
        assert observed == ["Mint111"]
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()
