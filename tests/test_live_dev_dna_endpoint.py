from __future__ import annotations

import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer

import src.web_snapshot as web_snapshot
from src.web_snapshot import build_developer_dna


TOKEN = "Mint111"
SIGNER = "FeePayer111"
AUTHORITY = "Authority111"
SIGNATURE = "MintInitSignature111"


class FakeRPC:
    def __init__(self):
        self.calls = []

    def get_signatures_for_address(self, address, *, limit=10, before=None, until=None, commitment="confirmed"):
        self.calls.append(("signatures", address, limit, commitment))
        return [{"signature": SIGNATURE, "err": None, "slot": 99}]

    def get_transaction(self, signature, *, commitment="confirmed", max_supported_transaction_version=1, encoding="jsonParsed"):
        self.calls.append(("transaction", signature, commitment))
        return {
            "slot": 99,
            "blockTime": 1_800_000_000,
            "meta": {"err": None, "innerInstructions": []},
            "transaction": {
                "signatures": [SIGNATURE],
                "message": {
                    "accountKeys": [
                        {"pubkey": SIGNER, "signer": True, "writable": True},
                        {"pubkey": AUTHORITY, "signer": False, "writable": False},
                    ],
                    "instructions": [{
                        "program": "spl-token",
                        "programId": "TokenProgram111",
                        "parsed": {
                            "type": "initializeMint",
                            "info": {"mint": TOKEN, "mintAuthority": AUTHORITY, "decimals": 6},
                        },
                    }],
                },
            },
        }


def test_dev_dna_reports_signer_candidate_without_claiming_developer_or_risk(monkeypatch):
    monkeypatch.delenv("SOLANA_RPC_URL", raising=False)
    rpc = FakeRPC()

    result = build_developer_dna(TOKEN, rpc_client=rpc, signature_limit=100, history_limit=40)

    assert result["status"] == "INITIALIZATION_OBSERVED"
    assert result["evidence_status"] == "SIGNER_CANDIDATE_ONLY"
    assert result["signer_candidate"] == SIGNER
    assert result["mint_authority"] == AUTHORITY
    assert result["initialization"]["signature"] == SIGNATURE
    assert result["risk_score"] is None
    assert result["classification"] == "NOT_SCORED"
    assert result["validation_status"] == "INSUFFICIENT_EVIDENCE"
    assert result["data_complete"] is True
    assert result["signer_history"]["other_mint_initializations_observed"] == 0


def test_dev_dna_requires_configured_rpc(monkeypatch):
    monkeypatch.delenv("SOLANA_RPC_URL", raising=False)

    result = build_developer_dna(TOKEN)

    assert result["status"] == "NOT_CONFIGURED"
    assert result["risk_score"] is None
    assert result["classification"] == "NOT_SCORED"


def test_dev_dna_route_returns_evidence(monkeypatch):
    payload = {"status": "INITIALIZATION_OBSERVED", "token": TOKEN, "risk_score": None}
    monkeypatch.setattr(web_snapshot, "build_developer_dna", lambda token: payload)
    server = ThreadingHTTPServer(("127.0.0.1", 0), web_snapshot.SnapshotHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/dev-dna?token={TOKEN}"
        with urllib.request.urlopen(url, timeout=2) as response:
            assert response.status == 200
            result = json.loads(response.read())
        assert result == payload
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()
