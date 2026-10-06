from src.manipulation import assess_manipulation
from src.wallets.clusters import detect_overlap_links
from src.wallets.graph import WalletGraph


def test_overlap_links_detect_repeated_token_overlap() -> None:
    graph = WalletGraph(
        wallet_to_tokens={
            "A": frozenset({"T1", "T2"}),
            "B": frozenset({"T1", "T2", "T3"}),
            "C": frozenset({"T9"}),
        },
        token_to_wallets={
            "T1": frozenset({"A", "B"}),
            "T2": frozenset({"A", "B"}),
            "T3": frozenset({"B"}),
            "T9": frozenset({"C"}),
        },
    )
    links = detect_overlap_links(graph, min_shared_tokens=2, min_confidence=0.4)
    assert len(links) == 1
    assert links[0].shared_tokens == 2


def test_manipulation_blocks_high_composite_risk() -> None:
    result = assess_manipulation(
        linked_wallet_ratio=0.9,
        synchronized_entry_ratio=0.8,
        holder_concentration_ratio=0.8,
        dev_sell_ratio=0.7,
    )
    assert result.blocked is True
    assert result.score >= 0.70


def test_manipulation_does_not_block_low_inputs() -> None:
    result = assess_manipulation(
        linked_wallet_ratio=0.1,
        synchronized_entry_ratio=0.1,
        holder_concentration_ratio=0.1,
        dev_sell_ratio=0.1,
    )
    assert result.blocked is False
