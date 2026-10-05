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
