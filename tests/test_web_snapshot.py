from dataclasses import replace
from datetime import datetime, timezone

from src.radar.models import TokenCandidate
from src.web_snapshot import build_snapshot


class FakeClient:
    def discover(self, max_tokens=10):
        return [
            TokenCandidate(
                address="Token111",
                observed_at=datetime.now(timezone.utc),
                source="test",
                symbol="TEST",
                name="Test Token",
                liquidity_usd=5000,
                market_cap_usd=25000,
                age_seconds=30,
                volume_5m_usd=1000,
                volume_1h_usd=5000,
                txn_count_5m=25,
                txn_count_1h=100,
                buy_txns_5m=17,
                sell_txns_5m=8,
                buy_txns_1h=70,
                sell_txns_1h=30,
            )
        ]


def test_build_snapshot_exposes_real_radar_fields_without_inventing_edge():
    snapshot = build_snapshot(FakeClient(), max_tokens=1)
    assert snapshot["status"] == "READY"
    assert snapshot["execution"] == "LOCKED"
    assert snapshot["validation_status"] == "INSUFFICIENT_EVIDENCE"
    assert snapshot["sources"]["dexscreener"]["status"] == "CONNECTED"
    assert snapshot["sources"]["solana_rpc"]["status"] == "NOT_CONFIGURED"
    item = snapshot["opportunities"][0]
    assert item["symbol"] == "TEST"
    assert item["volume_5m_usd"] == 1000.0
    assert item["volume_1h_usd"] == 5000.0
    assert item["txn_count_5m"] == 25
    assert item["txns_per_minute"] == 5.0
    assert item["buy_txns_5m"] == 17
    assert item["sell_txns_5m"] == 8
    assert item["buy_txns_1h"] == 70
    assert item["sell_txns_1h"] == 30
    assert item["decision"] == "WAIT"
    assert item["evidence_status"] == "MARKET_ACTIVITY_ONLY"
    assert item["smart_money_status"] == "NOT_EVALUATED"


def test_build_snapshot_fails_closed_on_data_error():
    class BrokenClient:
        def discover(self, max_tokens=10):
            raise RuntimeError("network")

    # Unexpected errors must remain visible rather than becoming fake readiness.
    try:
        build_snapshot(BrokenClient())
    except RuntimeError as exc:
        assert str(exc) == "network"
    else:
        raise AssertionError("unexpected errors must not be hidden")



def test_build_snapshot_reports_configured_solana_rpc_health():
    class FakeRPC:
        def get_health(self):
            return "ok"

        def get_slot(self):
            return 123456

    snapshot = build_snapshot(FakeClient(), max_tokens=1, rpc_client=FakeRPC())
    assert snapshot["sources"]["solana_rpc"] == {
        "status": "CONNECTED",
        "health": "ok",
        "slot": 123456,
    }



def test_snapshot_displays_real_candidates_when_all_fail_radar_policy():
    class OlderCandidateClient:
        def discover(self, max_tokens=10):
            return [replace(FakeClient().discover()[0], age_seconds=600)]

    snapshot = build_snapshot(OlderCandidateClient(), max_tokens=1)
    assert snapshot["discovery"] == {
        "discovered_candidate_count": 1,
        "qualifying_candidate_count": 0,
        "displayed_candidate_count": 1,
        "display_mode": "FILTERED_FALLBACK",
    }
    item = snapshot["opportunities"][0]
    assert item["symbol"] == "TEST"
    assert item["radar_eligibility"] == "FILTERED_BY_RADAR_POLICY"
    assert item["radar_filter_reasons"] == ["PAIR_AGE_EXCEEDS_MAX_AGE"]
    assert item["decision"] == "WAIT"
    assert snapshot["execution"] == "LOCKED"


def test_snapshot_route_accepts_ui_query_parameters(monkeypatch):
    from src import web_snapshot

    calls = []
    expected = {"status": "READY", "sources": {"solana_rpc": {"status": "NOT_CONFIGURED"}}}
    monkeypatch.setattr(web_snapshot, "build_snapshot", lambda client: expected)

    class HandlerStub:
        path = "/snapshot?ui=16&t=123"
        client = FakeClient()

        def _write_json(self, status, payload):
            calls.append((status, payload))

        def _serve_static(self, path):
            raise AssertionError(f"unexpected static route: {path}")

    web_snapshot.SnapshotHandler.do_GET(HandlerStub())
    assert calls == [(200, expected)]
