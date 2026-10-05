"""Pytest bootstrap for the repository source layout.

The project intentionally keeps application code under ./src.  This bootstrap
makes the repository root importable even when pytest is launched from an
environment that does not honor the configured pythonpath option.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
