"""Display helpers for notebook and script output."""

from __future__ import annotations

from pathlib import Path


def relative_path(path: object, *, base: Path | None = None) -> str:
    """Return a privacy-preserving path for logs and notebook output."""
    path_obj = Path(path)
    if base is None:
        base = Path.cwd()
    try:
        return str(path_obj.resolve().relative_to(base.resolve()))
    except Exception:
        return path_obj.name
