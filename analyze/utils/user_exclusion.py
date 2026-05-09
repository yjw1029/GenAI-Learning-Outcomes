"""
User exclusion utilities.

Some users are flagged as cheating/misconduct and should be excluded from all
analysis outputs. The canonical list lives at `data/processed/exclude_user.csv`.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, TypeVar

T = TypeVar("T")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_EXCLUDE_USER_FILE = PROJECT_ROOT / "data/processed/exclude_user.csv"


def load_excluded_usernames(path: Path | None = None) -> set[str]:
    """Load excluded usernames from `exclude_user.csv`.

    The CSV is expected to contain a `username` column (case-insensitive).
    """
    csv_path = path or DEFAULT_EXCLUDE_USER_FILE
    if not csv_path.exists():
        return set()

    excluded: set[str] = set()
    with csv_path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            if not isinstance(row, dict):
                continue
            username = (row.get("username") or row.get("账号") or "").strip()
            if username:
                excluded.add(username)
    return excluded


def filter_excluded_usernames(usernames: Iterable[str], excluded: set[str]) -> list[str]:
    """Filter a list/iterable of usernames, keeping only non-excluded ones."""
    return [u for u in usernames if isinstance(u, str) and u not in excluded]


def drop_excluded_from_dict(mapping: dict[str, T], excluded: set[str]) -> dict[str, T]:
    """Return a copy of mapping with excluded usernames removed."""
    if not excluded:
        return dict(mapping)
    return {k: v for k, v in mapping.items() if k not in excluded}
