from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class KillSwitchState:
    enabled: bool
    reason: str = ""

class KillSwitch:
    """Persistent safety latch; it never enables live execution."""
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
    def set(self, reason: str) -> None:
        if not reason.strip(): raise ValueError("reason is required")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(reason.strip(), encoding="utf-8")
    def clear(self) -> None:
        if self.path.exists(): self.path.unlink()
    def state(self) -> KillSwitchState:
        if not self.path.exists(): return KillSwitchState(False, "")
        return KillSwitchState(True, self.path.read_text(encoding="utf-8"))
