from src.wallets.counterparties import CounterpartyEvidence
from src.wallets.economic_links import WalletLinkEvidence
from src.wallets.manipulation_adapter import build_cluster_manipulation_input


def test_same_wallet_pair_is_counted_once_across_detectors():
    r = build_cluster_manipulation_input(
        wallet_count=3,
        wallet_links=(WalletLinkEvidence('A','B',3,1,0.8),),
        counterparties=(CounterpartyEvidence('A','B',3,3,0.9),),
    )
    assert r.linked_wallet_ratio == 1 / 3
