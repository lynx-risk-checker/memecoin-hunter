from __future__ import annotations

from typing import Protocol

from .models import TokenCandidate


class TokenSource(Protocol):
    name: str

    def discover(self) -> list[TokenCandidate]:
        """Return candidates observed from a real external source."""
