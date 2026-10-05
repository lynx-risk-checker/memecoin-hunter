from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClusterEvidence:
    shared_token_links: int
    synchronized_links: int
    counterparty_links: int
    strongest_confidence: float

    @property
    def score(self) -> float:
        # Stronger evidence gets more weight. This is a heuristic research score,
        # not proof that wallets share one economic owner.
        raw = (
            min(self.shared_token_links / 3.0, 1.0) * 0.20
            + min(self.synchronized_links / 3.0, 1.0) * 0.30
            + min(self.counterparty_links / 3.0, 1.0) * 0.35
            + self.strongest_confidence * 0.15
        )
        return min(1.0, raw)


def classify_cluster(evidence: ClusterEvidence) -> str:
    if evidence.score >= 0.75:
        return "HIGH_LINK_EVIDENCE"
    if evidence.score >= 0.45:
        return "MEDIUM_LINK_EVIDENCE"
    return "LOW_LINK_EVIDENCE"
