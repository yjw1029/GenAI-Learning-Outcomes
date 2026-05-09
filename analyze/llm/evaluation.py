"""LLM answer-evaluation loaders and difficulty summaries."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from analyze.config.scoring import MATH_SCORE_MAP, PY_SCORE_MAP

def _coerce_int_score(value: Any) -> Optional[int]:
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and value.strip().lstrip("-").isdigit():
        return int(value)
    return None


def _coerce_score_dict(value: Any) -> Optional[dict[str, int]]:
    if not isinstance(value, dict):
        return None
    coerced: dict[str, int] = {}
    for k, v in value.items():
        if not isinstance(k, str):
            return None
        iv = _coerce_int_score(v)
        if iv is None:
            return None
        coerced[k] = iv
    return coerced


MODEL_DISPLAY_NAMES = {
    "openai/gpt-4o": "GPT-4o",
    "openai/gpt-5": "GPT-5",
    "openai/gpt-4.1": "GPT-4.1",
    "anthropic/claude-sonnet-4.6": "Claude Sonnet 4.6",
    "anthropic/claude-3.7-sonnet": "Claude 3.7 Sonnet",
    "google/gemini-2.5-flash": "Gemini 2.5 Flash",
    "google/gemini-3-pro-preview": "Gemini 3 Pro",
    "google/gemini-3-flash-preview": "Gemini 3 Flash",
    "deepseek/deepseek-r1": "DeepSeek R1",
    "meta-llama/llama-4-maverick": "Llama 4 Maverick",
}


MODEL_ORDER = [
    "GPT-4o",
    "DeepSeek R1",
    "Claude 3.7 Sonnet",
    "Llama 4 Maverick",
    "GPT-4.1",
    "Gemini 2.5 Flash",
    "GPT-5",
    "Gemini 3 Pro",
    "Gemini 3 Flash",
    "Claude Sonnet 4.6",
]


def display_model_name(model: str) -> str:
    return MODEL_DISPLAY_NAMES.get(model, model)


def load_math_llm_reviews(path: Path, *, prefer_eval: bool = False) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(payload, dict):
        return []
    rows: list[dict[str, Any]] = []

    if prefer_eval:
        reviews = payload.get("math_eval")
        if isinstance(reviews, dict):
            for _, rec in reviews.items():
                if not isinstance(rec, dict):
                    continue
                evaluate = _coerce_score_dict(rec.get("evaluate"))
                if evaluate is None:
                    continue
                rows.append(
                    {
                        "pname": str(rec.get("pname") or ""),
                        "model": str(rec.get("model") or "unknown"),
                        "run_idx": rec.get("run_idx"),
                        "evaluate": evaluate,
                    }
                )
            return rows

    math_data = payload.get("math")
    if not isinstance(math_data, dict):
        return rows
    for pname, pdata in math_data.items():
        if not isinstance(pdata, dict):
            continue
        runs = pdata.get("runs")
        if not isinstance(runs, list):
            continue
        for idx, run in enumerate(runs):
            if not isinstance(run, dict):
                continue
            evaluate = _coerce_score_dict(run.get("evaluate"))
            if evaluate is None:
                continue
            rows.append(
                {
                    "pname": pname,
                    "model": str(run.get("model") or "unknown"),
                    "run_idx": run.get("run_idx", idx + 1),
                    "evaluate": evaluate,
                }
            )
    return rows


def compute_blank_points_map() -> dict[tuple[str, str], float]:
    out: dict[tuple[str, str], float] = {}
    for prob, wmap in MATH_SCORE_MAP.items():
        if not isinstance(wmap, dict):
            continue
        for blank, w in wmap.items():
            try:
                out[(prob, str(blank))] = float(w)
            except Exception:
                continue
    return out


def assign_difficulty_thresholds(
    blank_points: dict[tuple[str, str], float],
    *,
    easy_max: float,
    medium_max: float,
) -> dict[tuple[str, str], str]:
    out: dict[tuple[str, str], str] = {}
    for key, pts in blank_points.items():
        if pts < easy_max:
            out[key] = "Easy"
        elif pts <= medium_max:
            out[key] = "Medium"
        else:
            out[key] = "Hard"
    return out


def summarize_llm_scores_by_difficulty(
    reviews: list[dict[str, Any]],
    blank_points: dict[tuple[str, str], float],
    blank_difficulty: dict[tuple[str, str], str],
) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    accum: dict[str, dict[str, dict[str, float]]] = {}

    for rec in reviews:
        pname = rec.get("pname")
        model = rec.get("model")
        evaluate = rec.get("evaluate")
        if not isinstance(pname, str) or not isinstance(model, str) or not isinstance(evaluate, dict):
            continue
        for blank_id, score in evaluate.items():
            pts = blank_points.get((pname, str(blank_id)))
            if pts is None:
                continue
            diff = blank_difficulty.get((pname, str(blank_id)))
            if diff is None:
                continue
            model_map = accum.setdefault(model, {})
            diff_map = model_map.setdefault(diff, {"score": 0.0, "total": 0.0})
            diff_map["total"] += float(pts)
            if int(score) == 1:
                diff_map["score"] += float(pts)

    for model, diffs in accum.items():
        for diff, vals in diffs.items():
            total = float(vals.get("total", 0.0))
            scored = float(vals.get("score", 0.0))
            records.append(
                {
                    "model": model,
                    "difficulty": diff,
                    "score_points": scored,
                    "total_points": total,
                    "accuracy": (scored / total) if total > 0 else math.nan,
                }
            )

    return pd.DataFrame(records)


def load_python_llm_runs(path: Path, *, prefer_eval: bool = False) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    if not isinstance(payload, dict):
        return []
    if prefer_eval:
        py_runs = payload.get("python_eval")
        if not isinstance(py_runs, list):
            return []
        rows: list[dict[str, Any]] = []
        for run in py_runs:
            if not isinstance(run, dict):
                continue
            pname = run.get("pname")
            if not isinstance(pname, str):
                continue
            max_score = PY_SCORE_MAP.get(pname)
            if max_score is None:
                continue
            passed = run.get("passed")
            if not isinstance(passed, bool):
                continue
            rows.append(
                {
                    "pname": pname,
                    "model": str(run.get("model") or "unknown"),
                    "passed": passed,
                    "max_score": int(max_score),
                }
            )
        return rows

    py_data = payload.get("python")
    if not isinstance(py_data, dict):
        return []
    rows: list[dict[str, Any]] = []
    for pname, pdata in py_data.items():
        if not isinstance(pdata, dict):
            continue
        runs = pdata.get("runs")
        if not isinstance(runs, list):
            continue
        max_score = PY_SCORE_MAP.get(pname)
        if max_score is None:
            continue
        for run in runs:
            if not isinstance(run, dict):
                continue
            evaluate = run.get("evaluate")
            if not isinstance(evaluate, dict):
                continue
            passed = evaluate.get("passed")
            if not isinstance(passed, bool):
                continue
            rows.append(
                {
                    "pname": pname,
                    "model": str(run.get("model") or "unknown"),
                    "passed": passed,
                    "max_score": int(max_score),
                }
            )
    return rows


def summarize_python_llm_accuracy_by_difficulty(runs: list[dict[str, Any]]) -> pd.DataFrame:
    def _difficulty(ms: Optional[int]) -> Optional[str]:
        if ms is None:
            return None
        if ms in (1, 2):
            return "Easy"
        if ms == 3:
            return "Medium"
        if ms in (4, 5):
            return "Hard"
        return None

    counts: dict[str, dict[str, list[int]]] = {}
    for rec in runs:
        ms = rec.get("max_score")
        d = _difficulty(ms if isinstance(ms, int) else None)
        if d is None:
            continue
        model = rec.get("model")
        if not isinstance(model, str):
            continue
        entry = counts.setdefault(model, {}).setdefault(d, [0, 0])
        entry[0] += 1 if rec.get("passed") else 0
        entry[1] += 1

    records: list[dict[str, Any]] = []
    for model, diffs in counts.items():
        for diff, (k, n) in diffs.items():
            records.append(
                {
                    "model": model,
                    "difficulty": diff,
                    "n_correct": k,
                    "n_total": n,
                    "accuracy": (k / n) if n else math.nan,
                }
            )
    return pd.DataFrame(records)
