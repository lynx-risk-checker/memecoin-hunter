from __future__ import annotations

import os
from dataclasses import dataclass, field


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    app_env: str = field(default_factory=lambda: _env("APP_ENV", "development"))
    dry_run: bool = field(default_factory=lambda: _bool("DRY_RUN", True))
    paper_trading: bool = field(default_factory=lambda: _bool("PAPER_TRADING", True))
    solana_rpc_url: str = field(default_factory=lambda: _env("SOLANA_RPC_URL", ""))
    max_position_usd: float = field(
        default_factory=lambda: float(_env("MAX_POSITION_USD", "10"))
    )
    max_daily_loss_usd: float = field(
        default_factory=lambda: float(_env("MAX_DAILY_LOSS_USD", "10"))
    )
    max_slippage_bps: int = field(
        default_factory=lambda: int(_env("MAX_SLIPPAGE_BPS", "100"))
    )

    def validate(self) -> None:
        if not self.dry_run and self.paper_trading:
            raise ValueError("PAPER_TRADING cannot be enabled while DRY_RUN is disabled.")
        if self.max_position_usd <= 0:
            raise ValueError("MAX_POSITION_USD must be positive.")
        if self.max_daily_loss_usd <= 0:
            raise ValueError("MAX_DAILY_LOSS_USD must be positive.")
        if not 0 <= self.max_slippage_bps <= 10_000:
            raise ValueError("MAX_SLIPPAGE_BPS must be between 0 and 10000.")
