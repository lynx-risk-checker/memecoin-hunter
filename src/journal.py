from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

@dataclass(frozen=True)
class JournalEvent:
    event_type: str
    timestamp: int
    token: str
    payload: dict[str, object]

class PaperJournal:
    """Append-only JSONL journal for paper decisions and completed trades."""
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
    def append(self, event: JournalEvent) -> None:
        if not event.event_type.strip() or not event.token.strip():
            raise ValueError("event_type and token are required")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(event), sort_keys=True) + "\n")
    def read(self) -> tuple[JournalEvent, ...]:
        if not self.path.exists():
            return ()
        events=[]
        with self.path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    raw=json.loads(line)
                    events.append(JournalEvent(str(raw["event_type"]),int(raw["timestamp"]),str(raw["token"]),dict(raw.get("payload",{}))))
        return tuple(events)
    def append_many(self, events: Iterable[JournalEvent]) -> None:
        for event in events:
            self.append(event)
