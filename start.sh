#!/usr/bin/env sh
set -eu

# Railway/Railpack compatibility entry point.
# Keep this aligned with the repository Dockerfile startup command.
exec python -m src.web_snapshot
