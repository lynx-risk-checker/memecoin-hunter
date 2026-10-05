from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Mission:
    start_idr: int = 100_000
    target_idr: int = 1_500_000

    def progress(self, capital_idr: int) -> float:
        if self.target_idr <= self.start_idr:
            return 1.0
        return max(
            0.0,
            min(1.0, (capital_idr - self.start_idr) / (self.target_idr - self.start_idr)),
        )

    def status(self, capital_idr: int) -> str:
        return "TARGET_REACHED" if capital_idr >= self.target_idr else "IN_PROGRESS"


MISSIONS: tuple[Mission, ...] = (
    Mission(1_000, 1_500_000),
    Mission(1_500_000, 5_000_000),
    Mission(5_000_000, 25_000_000),
    Mission(25_000_000, 100_000_000),
    Mission(100_000_000, 500_000_000),
    Mission(500_000_000, 1_000_000_000),
)
