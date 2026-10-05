from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PaperTrade:
    token: str
    entry_usd: float
    exit_usd: float
    position_usd: float

    @property
    def pnl_usd(self) -> float:
        if self.entry_usd <= 0 or self.exit_usd < 0 or self.position_usd <= 0:
            raise ValueError("invalid trade values")
        return self.position_usd * ((self.exit_usd / self.entry_usd) - 1.0)


def summarize(trades: list[PaperTrade]) -> dict[str, float]:
    if not trades:
        return {"trades": 0.0, "pnl_usd": 0.0, "win_rate": 0.0}
    pnls = [trade.pnl_usd for trade in trades]
    return {
        "trades": float(len(trades)),
        "pnl_usd": sum(pnls),
        "win_rate": sum(pnl > 0 for pnl in pnls) / len(pnls),
    }
