import os

import pytest

from src.config import Settings


def test_paper_mode_cannot_disable_dry_run(monkeypatch):
    monkeypatch.setenv("DRY_RUN", "false")
    monkeypatch.setenv("PAPER_TRADING", "true")
    with pytest.raises(ValueError, match="PAPER_TRADING"):
        Settings().validate()
