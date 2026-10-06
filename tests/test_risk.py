from src.risk import veto


def base(**overrides):
    values = dict(
        dry_run=True,
        paper_trading=True,
        expected_value=1.0,
        daily_loss=0,
        max_daily_loss=10,
        position_usd=5,
        max_position_usd=10,
        slippage_bps=50,
        max_slippage_bps=100,
    )
    values.update(overrides)
    return veto(**values)


def test_positive_ev_is_allowed_in_paper():
    assert base().allowed


def test_non_positive_ev_is_blocked():
    assert not base(expected_value=0).allowed
    assert base(expected_value=0).reason == "EV_NON_POSITIVE"


def test_position_limit_blocks():
    assert not base(position_usd=11).allowed


def test_slippage_limit_blocks():
    assert not base(slippage_bps=101).allowed


def test_daily_loss_limit_blocks():
    assert not base(daily_loss=10).allowed


def test_live_is_not_implemented():
    decision = base(dry_run=False, paper_trading=False)
    assert not decision.allowed
    assert decision.reason == "LIVE_EXECUTION_NOT_IMPLEMENTED"
