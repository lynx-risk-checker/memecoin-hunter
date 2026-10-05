from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExecutionRequest:
    token: str
    position_usd: float
    slippage_bps: int


class ExecutionLockedError(RuntimeError):
    pass


class ExecutionEngine:
    """Safety boundary. Live order placement is intentionally unavailable."""

    def execute(self, request: ExecutionRequest) -> None:
        raise ExecutionLockedError("LIVE_EXECUTION_LOCKED")
