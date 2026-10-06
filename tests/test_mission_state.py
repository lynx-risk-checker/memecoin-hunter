from src.mission_state import evaluate_mission


def test_mission_state_starts_at_first_mission() -> None:
    state = evaluate_mission(1_000)
    assert state.mission_index == 0
    assert state.status == "IN_PROGRESS"


def test_mission_state_advances_by_capital() -> None:
    state = evaluate_mission(1_500_000)
    assert state.mission_index == 1
    assert state.status == "IN_PROGRESS"


def test_mission_state_caps_at_final_mission() -> None:
    state = evaluate_mission(1_000_000_000)
    assert state.mission_index == 5
    assert state.status == "TARGET_REACHED"
