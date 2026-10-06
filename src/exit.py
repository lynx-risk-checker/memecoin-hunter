from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ProtectionState(StrEnum):
    NORMAL = "NORMAL"
    CAUTION = "CAUTION"
    DEFENSIVE = "DEFENSIVE"
    HALTED = "HALTED"


@dataclass(frozen=True)
class ExitSignal:
    emergency: bool
    reasons: tuple[str, ...]


def evaluate_protection(
    *,
    state: ProtectionState,
    liquidity_drop_pct: float,
    dev_sell_ratio: float,
    manipulation_blocked: bool,
    exitability: bool,
) -> ExitSignal:
    if liquidity_drop_pct < 0:
        raise ValueError("liquidity_drop_pct cannot be negative")
    if not 0 <= dev_sell_ratio <= 1:
        raise ValueError("dev_sell_ratio must be between 0 and 1")

    reasons: list[str] = []
    if state == ProtectionState.HALTED:
        reasons.append("MISSION_HALTED")
    if liquidity_drop_pct >= 50:
        reasons.append("LIQUIDITY_COLLAPSE")
    if dev_sell_ratio >= 0.70:
        reasons.append("DEV_SELL_PRESSURE")
    if manipulation_blocked:
        reasons.append("MANIPULATION_RISK")
    if not exitability:
        reasons.append("EXITABILITY_LOST")
    return ExitSignal(bool(reasons), tuple(reasons))
