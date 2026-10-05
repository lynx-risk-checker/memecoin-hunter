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
    funding_link_ratio: float = 0.0,
    threshold: float = 0.70,
) -> ManipulationAssessment:
    values = (
        linked_wallet_ratio, synchronized_entry_ratio,
        holder_concentration_ratio, dev_sell_ratio,
        funding_link_ratio, threshold,
    )
    if any(not 0 <= value <= 1 for value in values):
        raise ValueError("manipulation inputs must be between 0 and 1")

    base_score = (
        0.20 * linked_wallet_ratio
        + 0.25 * synchronized_entry_ratio
        + 0.20 * holder_concentration_ratio
        + 0.15 * dev_sell_ratio
    )
    # Funding evidence is optional. If absent, normalize the available
    # four-signal composite rather than silently assigning it zero risk.
    score = (
        base_score + 0.20 * funding_link_ratio
        if funding_link_ratio > 0
        else base_score / 0.80
    )

    reasons: list[str] = []
    if linked_wallet_ratio >= 0.70:
        reasons.append("HIGH_LINKED_WALLETS")
    if synchronized_entry_ratio >= 0.70:
        reasons.append("HIGH_SYNCHRONIZED_ACTIVITY")
    if holder_concentration_ratio >= 0.70:
        reasons.append("HIGH_HOLDER_CONCENTRATION")
    if dev_sell_ratio >= 0.70:
        reasons.append("HIGH_DEV_SELL_ACTIVITY")
    if funding_link_ratio >= 0.70:
        reasons.append("HIGH_SHARED_FUNDING_LINK")

    blocked = score >= threshold or funding_link_ratio >= 0.85
    if blocked:
        reasons.append("MANIPULATION_RISK_BLOCK")

    return ManipulationAssessment(score=score, blocked=blocked, reasons=tuple(reasons))
