from __future__ import annotations

import json
from pathlib import Path

from src.mission_state import MissionState


class MissionStateStore:
    """Small atomic JSON state store for paper/mission mode; never enables live execution."""
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def save(self, state: MissionState) -> None:
        if state.capital_idr < 0:
            raise ValueError("capital_idr cannot be negative")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(
            json.dumps(
                {
                    "capital_idr": state.capital_idr,
                    "mission_index": state.mission_index,
                    "status": state.status,
                },
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        tmp.replace(self.path)

    def load(self) -> MissionState | None:
        if not self.path.exists():
            return None
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return MissionState(
            capital_idr=int(raw["capital_idr"]),
            mission_index=int(raw["mission_index"]),
            status=str(raw["status"]),
        )
