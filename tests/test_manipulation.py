from src.manipulation import assess_manipulation


def test_shared_funding_can_block_manipulation() -> None:
    result = assess_manipulation(
        linked_wallet_ratio=0.10,
        synchronized_entry_ratio=0.10,
        holder_concentration_ratio=0.10,
        dev_sell_ratio=0.10,
        funding_link_ratio=0.90,
    )
    assert result.blocked is True
    assert "HIGH_SHARED_FUNDING_LINK" in result.reasons
    assert "MANIPULATION_RISK_BLOCK" in result.reasons


def test_cleaner_activity_is_not_blocked() -> None:
    result = assess_manipulation(
        linked_wallet_ratio=0.05,
        synchronized_entry_ratio=0.05,
        holder_concentration_ratio=0.10,
        dev_sell_ratio=0.05,
        funding_link_ratio=0.05,
    )
    assert result.blocked is False
