from __future__ import annotations

from src.journal import JournalEvent
from src.paper_metrics import PaperPerformance, PaperTradeRecord, summarize_performance


def trade_records_from_journal(events: tuple[JournalEvent, ...]) -> tuple[PaperTradeRecord, ...]:
    records = []
    for event in events:
        if event.event_type != "TRADE":
            continue
        payload = event.payload
        records.append(
            PaperTradeRecord(
                token=event.token,
                pnl_usd=float(payload["pnl_usd"]),
                position_usd=float(payload["position_usd"]),
                slippage_bps=float(payload.get("slippage_bps", 0.0)),
                latency_ms=float(payload.get("latency_ms", 0.0)),
                rug_loss=bool(payload.get("rug_loss", False)),
            )
        )
    return tuple(records)


def performance_from_journal(
    events: tuple[JournalEvent, ...], *, starting_equity_usd: float
) -> PaperPerformance:
    return summarize_performance(
        list(trade_records_from_journal(events)), starting_equity_usd
    )
