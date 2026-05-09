"""
Utilities for computing math (game theory) homework scores.

The LLM review JSON currently stores per-problem fields under a nested "scores" dict,
e.g.:
  data[username][problem] = {"scores": {"填空1": 1, ...}, ...}

Some older pipelines may store the score dict directly at data[username][problem].
This module supports both formats.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping


def _is_correct_flag(value: Any) -> bool:
    if value is True:
        return True
    if value is False or value is None:
        return False
    if isinstance(value, (int, float)):
        try:
            return float(value) == 1.0
        except Exception:
            return False
    if isinstance(value, str):
        return value.strip().lower() in {"1", "1.0", "true", "yes", "y"}
    return False


def _extract_score_dict(problem_data: Any) -> Mapping[str, Any]:
    if not isinstance(problem_data, dict):
        return {}
    nested = problem_data.get("scores")
    if isinstance(nested, dict):
        return nested
    return problem_data


def load_math_hw_scores(
    path: Path,
    *,
    hw1_problems: list[str],
    hw2_problems: list[str],
    score_map: dict[str, dict[str, float]],
) -> dict[str, dict[str, float]]:
    if not path.exists():
        return {}

    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)

    scores: dict[str, dict[str, float]] = {}
    if not isinstance(data, dict):
        return scores

    for username, problems in data.items():
        if not isinstance(username, str) or not isinstance(problems, dict):
            continue

        hw1_score = 0.0
        hw2_score = 0.0

        for problem in hw1_problems:
            if problem not in problems or problem not in score_map:
                continue
            score_dict = _extract_score_dict(problems.get(problem))
            for field, points in score_map[problem].items():
                if _is_correct_flag(score_dict.get(field)):
                    hw1_score += points

        for problem in hw2_problems:
            if problem not in problems or problem not in score_map:
                continue
            score_dict = _extract_score_dict(problems.get(problem))
            for field, points in score_map[problem].items():
                if _is_correct_flag(score_dict.get(field)):
                    hw2_score += points

        scores[username] = {"hw1_score": hw1_score, "hw2_score": hw2_score}

    return scores


if __name__ == "__main__":
    # Lightweight sanity check for local debugging.
    from analyze.config import MATH_HW1_PROBLEMS, MATH_HW2_PROBLEMS, MATH_SCORE_FILE, MATH_SCORE_MAP

    computed = load_math_hw_scores(
        Path(MATH_SCORE_FILE),
        hw1_problems=list(MATH_HW1_PROBLEMS),
        hw2_problems=list(MATH_HW2_PROBLEMS),
        score_map=dict(MATH_SCORE_MAP),
    )
    nonzero = sum(
        1
        for row in computed.values()
        if (row.get("hw1_score") or 0) > 0 or (row.get("hw2_score") or 0) > 0
    )
    print(f"Loaded {len(computed)} users; nonzero={nonzero}")
