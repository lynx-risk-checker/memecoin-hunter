from src.mission import MISSIONS
from src.mission_state import MissionState
from src.mission_store import MissionStateStore


def test_mission_state_round_trips(tmp_path):
    store = MissionStateStore(tmp_path / "mission.json")
    state = MissionState(capital_idr=1500, mission_index=0, status=MISSIONS[0].status(1500))
    store.save(state)
    assert store.load() == state


def test_missing_mission_state_is_none(tmp_path):
    assert MissionStateStore(tmp_path / "missing.json").load() is None


def test_mission_state_store_rejects_invalid_index(tmp_path):
    store = MissionStateStore(tmp_path / "mission.json")
    try:
        store.save(MissionState(capital_idr=1000, mission_index=999, status="NORMAL"))
    except ValueError as exc:
        assert "mission_index" in str(exc)
    else:
        raise AssertionError("invalid mission index was accepted")
