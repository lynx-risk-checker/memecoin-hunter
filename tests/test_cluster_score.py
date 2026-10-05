from src.wallets.cluster_score import ClusterEvidence, classify_cluster


def test_cluster_score_requires_multiple_evidence_types() -> None:
    weak = ClusterEvidence(3, 0, 0, 0.0)
    strong = ClusterEvidence(3, 3, 3, 0.9, 3)
    assert classify_cluster(weak) == "LOW_LINK_EVIDENCE"
    assert classify_cluster(strong) == "HIGH_LINK_EVIDENCE"
