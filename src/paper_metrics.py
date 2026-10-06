from __future__ import annotations

from dataclasses import dataclass
from math import inf


@dataclass(frozen=True)
class PaperTradeRecord:
    token: str
    pnl_usd: float
    position_usd: float
    slippage_bps: float = 0.0
    latency_ms: float = 0.0
    rug_loss: bool = False

    def __post_init__(self) -> None:
        if not self.token.strip():
            raise ValueError("token is required")
        if self.position_usd <= 0:
            raise ValueError("position_usd must be positive")
        if self.slippage_bps < 0 or self.latency_ms < 0:
            raise ValueError("execution metrics cannot be negative")


@dataclass(frozen=True)
class PaperPerformance:
    trades: int
    pnl_usd: float
    win_rate: float
    average_win_usd: float
    average_loss_usd: float
    expectancy_usd: float
    profit_factor: float
    max_drawdown_usd: float
    max_drawdown_pct: float
    rug_losses: int
    average_slippage_bps: float
    average_latency_ms: float


def summarize_performance(trades: list[PaperTradeRecord], starting_equity_usd: float) -> PaperPerformance:
    if starting_equity_usd <= 0:
        raise ValueError("starting_equity_usd must be positive")
    if not trades:
        return PaperPerformance(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0.0, 0.0)

    pnls = [trade.pnl_usd for trade in trades]
    wins = [pnl for pnl in pnls if pnl > 0]
    losses = [pnl for pnl in pnls if pnl < 0]
    gross_profit = sum(wins)
    gross_loss = -sum(losses)

    equity = starting_equity_usd
    peak = equity
    max_dd = 0.0
    max_dd_pct = 0.0
    for pnl in pnls:
        equity += pnl
        peak = max(peak, equity)
        drawdown = max(0.0, peak - equity)
        max_dd = max(max_dd, drawdown)
        max_dd_pct = max(max_dd_pct, drawdown / peak if peak else 0.0)

    profit_factor = gross_profit / gross_loss if gross_loss else (inf if gross_profit else 0.0)
    average_win = gross_profit / len(wins) if wins else 0.0
    average_loss = sum(losses) / len(losses) if losses else 0.0

    return PaperPerformance(
        trades=len(trades),
        pnl_usd=sum(pnls),
        win_rate=len(wins) / len(pnls),
        average_win_usd=average_win,
        average_loss_usd=average_loss,
        expectancy_usd=sum(pnls) / len(pnls),
        profit_factor=profit_factor,
        max_drawdown_usd=max_dd,
        max_drawdown_pct=max_dd_pct,
        rug_losses=sum(trade.rug_loss for trade in trades),
        average_slippage_bps=sum(t.slippage_bps for t in trades) / len(trades),
        average_latency_ms=sum(t.latency_ms for t in trades) / len(trades),
    )
