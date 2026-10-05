from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ManipulationAssessment:
    score: float
    blocked: bool
    reasons: tuple[str, ...]


def assess_manipulation(
    *,
    linked_wallet_ratio: float,
    synchronized_entry_ratio: float,
    holder_concentration_ratio: float,
    dev_sell_ratio: float,
    threshold: float = 0.70,
) -> ManipulationAssessment:
    values = (
        linked_wallet_ratio,
        synchronized_entry_ratio,
        holder_concentration_ratio,
        dev_sell_ratio,
        threshold,
    )
    if any(not 0 <= value <= 1 for value in values):
        raise ValueError("manipulation inputs must be between 0 and 1")

    score = (
        0.30 * linked_wallet_ratio
        + 0.25 * synchronized_entry_ratio
        + 0.25 * holder_concentration_ratio
        + 0.20 * dev_sell_ratio
    )
    reasons: list[str] = []
    if linked_wallet_ratio >= 0.5:
        reasons.append("LINKED_WALLETS")
    if synchronized_entry_ratio >= 0.5:
        reasons.append("SYNCHRONIZED_ENTRIES")
    if holder_concentration_ratio >= 0.5:
        reasons.append("HOLDER_CONCENTRATION")
    if dev_sell_ratio >= 0.5:
        reasons.append("DEV_SELL_PRESSURE")
    return ManipulationAssessment(
        score=score,
        blocked=score >= threshold,
        reasons=tuple(reasons),
    )
