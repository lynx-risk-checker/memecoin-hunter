from src.mission import Mission


def test_mission_progress_and_status():
    mission = Mission()
    assert mission.progress(100_000) == 0
    assert mission.status(1_500_000) == "TARGET_REACHED"
    assert mission.progress(800_000) == (800_000 - 100_000) / (1_500_000 - 100_000)
