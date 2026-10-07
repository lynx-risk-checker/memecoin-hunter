from src.kill_switch import KillSwitch

def test_kill_switch_persists_and_clears(tmp_path):
    switch = KillSwitch(tmp_path / "kill")
    assert switch.state().enabled is False
    switch.set("manual emergency")
    assert switch.state().enabled is True
    assert switch.state().reason == "manual emergency"
    switch.clear()
    assert switch.state().enabled is False
