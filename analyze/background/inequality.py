"""Helper functions for the reviewer-facing inequality notebook."""
#!/usr/bin/env python3
#%%
"""
Combined analysis plots runner (block-executable).

Block 1: Equity + A1 behavior proportions (Experiment only)
Block 2: Python A1 behavior analysis
Block 3: Math A1 behavior analysis

Note: This file is fully inlined and does not rely on runpy.
"""
import csv
import json
import math
import os
import statistics
import sys
import warnings
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import statsmodels.formula.api as smf
from statsmodels.stats.proportion import proportions_ztest

from analyze.utils.display import relative_path
import analyze.behavior.a1 as behavior_a1
from analyze.behavior.category_rules import (
    MATH_A1_DISPLAY_NAMES,
    MATH_A1_DISPLAY_ORDER,
    MATH_A1_PRECEDENCE,
    PYTHON_A1_DISPLAY_NAMES,
    PYTHON_A1_DISPLAY_ORDER,
    PYTHON_A1_PRECEDENCE,
    behavior_supergroup,
    pick_math_a1_category,
    pick_python_a1_category,
)

warnings.filterwarnings(
    "ignore",
    message="This figure includes Axes that are not compatible with tight_layout",
    category=UserWarning,
)

# Add project root to path by walking upward from this module or the notebook
# working directory. This keeps imports stable after moving code into packages.
def _find_repo_root() -> Path:
    starts = []
    if "__file__" in globals():
        starts.append(Path(__file__).resolve())
    starts.append(Path.cwd().resolve())
    for start in starts:
        for candidate in (start, *start.parents):
            if (candidate / "pyproject.toml").exists() and (candidate / "analyze").exists():
                return candidate
    return Path.cwd().resolve()

REPO_ROOT = _find_repo_root()
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

def _data_path(*candidates: str) -> Path:
    """Return the first existing data path, allowing old/new project layouts."""
    checked: list[Path] = []
    for candidate in candidates:
        path = Path(candidate)
        if not path.is_absolute():
            path = REPO_ROOT / candidate
        checked.append(path)
        if path.exists():
            return path
    return checked[0]


from analyze.config import (
    PRESURVEY_FILE,
    VALIDUSER_FILE,
    MATH_SCORE_MAP,
    MATH_HW1_PROBLEMS,
    MATH_HW2_PROBLEMS,
    CONTROL_COLOR,
    EXPERIMENT_COLOR,
    DIFF_COLOR,
    FIGURES_DIR,
    PYTHON_SCORE_FILE,
    MATH_SCORE_FILE,
)
from analyze.core import (
    load_presurvey_data,
    load_valid_users,
    load_capability_scores,
    load_homework_scores,
    merge_presurvey_to_df,
    prepare_covariates,
)
from analyze.config.scoring import MATH_HW1_PROBLEMS as MATH_HW1_PROBLEMS_CFG
from analyze.config.scoring import MATH_HW2_PROBLEMS as MATH_HW2_PROBLEMS_CFG
from analyze.config.scoring import MATH_SCORE_MAP as MATH_SCORE_MAP_CFG
from analyze.utils.math_scoring import load_math_hw_scores

# Global figure display toggle (set False for headless/script runs).
SHOW_FIGURES = True

# Override figure output directory for this script only.
FIGURES_DIR = REPO_ROOT / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

#%%
# =========================
# Block 1: Equity + behavior proportions
# =========================
# A1 behavior-group proportions (Experiment only, Python + Math)

LABEL_TRIED_Y = "y"
LABEL_TRIED_N = "n"
VERBATIM_MODES = {"copy", "type"}
COPYLIKE_MODES = {"copy", "type", "mix"}
EXPLAIN_GOALS = {"explain"}
EXPLAIN_TYPES = {"concept"}
FINAL_ANSWER_GOALS = {"final_answer"}
FINAL_ANSWER_TYPES = {"answer"}

# Same defaults as analyze/a1_behavior_analyze_py.py
TRIED_THRESHOLD = 0.25
COPY_FIRST_THRESHOLD = 0.75
PRECEDENCE = PYTHON_A1_PRECEDENCE

# Math behavior analysis defaults (see analyze/a1_behavior_analyze_math.py)
MATH_TRIED_THRESHOLD = 0.5
MATH_COPY_FIRST_THRESHOLD = 0.5
MATH_PRETRY_BLANK_PROP_THRESHOLD = 0.8
MATH_PRECEDENCE = MATH_A1_PRECEDENCE
MATH_VERBATIM_MODES = VERBATIM_MODES


def _set_nature_style_like_a1_behavior_analyze() -> None:
    """
    Match the style used by analyze/a1_behavior_analyze_py.py for publication-ready figures.
    """
    matplotlib.rcParams.update(
        {
            "figure.dpi": 300,
            "savefig.dpi": 300,
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 12,
            "axes.labelsize": 14,
            "axes.titlesize": 14,
            "xtick.labelsize": 12,
            "ytick.labelsize": 12,
            "axes.linewidth": 1.2,
            "xtick.major.width": 1.2,
            "ytick.major.width": 1.2,
            "xtick.major.size": 5.0,
            "ytick.major.size": 5.0,
            "xtick.direction": "out",
            "ytick.direction": "out",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.unicode_minus": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def _set_nature_style_v2() -> None:
    _set_nature_style_like_a1_behavior_analyze()


@dataclass(frozen=True)
class _A1ChatLabel:
    timestamp: float
    problem: str
    pre_tried: str
    ask_type: str
    ask_goal: str
    post_mode: str


@dataclass(frozen=True)
class _MathChatLabel:
    timestamp: float
    problem: str
    pre_tried: str
    ask_type: str
    ask_goal: str
    post_mode: str
    llm_wrong: bool
    post_has_correct: bool
    ask_blanks: dict
    post_blanks: dict
    pre_blanks: dict


def _is_enum_placeholder(value: object) -> bool:
    if value is None:
        return True
    s = str(value).strip()
    if not s:
        return True
    return "|" in s


def _norm_label(value: object, default: str = "unk") -> str:
    if value is None:
        return default
    s = str(value).strip()
    if not s:
        return default
    if _is_enum_placeholder(s):
        return default
    return s


def _safe_get(d: dict, path: tuple[str, ...], default: object = None) -> object:
    cur: object = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def _parse_correct_flag(value: object) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        if math.isnan(float(value)):
            return None
        return bool(int(value))
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"1", "y", "yes", "true"}:
            return True
        if v in {"0", "n", "no", "false"}:
            return False
    return None


def _blanks_any_correct(blanks: object, *, want_correct: bool) -> bool:
    if not isinstance(blanks, dict):
        return False
    for _k, v in blanks.items():
        if not isinstance(v, dict):
            continue
        flag = _parse_correct_flag(v.get("correct"))
        if flag is None:
            continue
        if flag is want_correct:
            return True
    return False


def _blanks_by_correct(blanks: object) -> tuple[set[str], set[str]]:
    correct_set: set[str] = set()
    wrong_set: set[str] = set()
    if not isinstance(blanks, dict):
        return correct_set, wrong_set
    for k, v in blanks.items():
        if not isinstance(v, dict):
            continue
        flag = _parse_correct_flag(v.get("correct"))
        if flag is None:
            continue
        if flag:
            correct_set.add(str(k))
        else:
            wrong_set.add(str(k))
    return correct_set, wrong_set


def _blank_attempted(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    return True


def _pretry_rate_for_problem(problem_id: str, chats_in_problem: list["_MathChatLabel"]) -> float | None:
    try:
        blanks_map = MATH_SCORE_MAP.get(problem_id, {})
    except Exception:
        blanks_map = {}
    total_blanks = len(list(blanks_map.keys())) if isinstance(blanks_map, dict) else 0
    if total_blanks <= 0:
        return None

    attempted: set[str] = set()
    for c in chats_in_problem:
        if not isinstance(c.pre_blanks, dict):
            continue
        for k, v in c.pre_blanks.items():
            if not isinstance(v, dict):
                continue
            if _blank_attempted(v.get("value")):
                attempted.add(str(k))
    return len(attempted) / total_blanks


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}


def _infer_target_problems_from_labels(labels_by_user: dict, *, stage: str, problem_prefix: str) -> list[str]:
    probs: set[str] = set()
    for _uid, user_blob in labels_by_user.items():
        if not isinstance(user_blob, dict):
            continue
        for _chat_action_id, rec in user_blob.items():
            if not isinstance(rec, dict):
                continue
            if stage and rec.get("stage") != stage:
                continue
            action = rec.get("action", "")
            if not (isinstance(action, str) and action.endswith("::chat")):
                continue
            problem = rec.get("problem") or (action.split("::", 1)[0] if "::" in action else action)
            if not (isinstance(problem, str) and problem.startswith(problem_prefix)):
                continue
            probs.add(problem)
    return sorted(probs)


def _iter_user_a1_chat_labels(
    labels_by_user: dict,
    user_id: str,
    *,
    stage: str,
    problem_prefix: str,
    drop_unk_ask: bool,
) -> list[_A1ChatLabel]:
    user_blob = labels_by_user.get(user_id, {})
    if not isinstance(user_blob, dict) or not user_blob:
        return []

    out: list[_A1ChatLabel] = []
    for _action_id, rec in user_blob.items():
        if not isinstance(rec, dict):
            continue
        if stage and rec.get("stage") != stage:
            continue
        action = rec.get("action", "")
        if not (isinstance(action, str) and action.endswith("::chat")):
            continue
        problem = rec.get("problem") or (action.split("::", 1)[0] if "::" in action else action)
        if not (isinstance(problem, str) and problem.startswith(problem_prefix)):
            continue
        label = rec.get("label") or {}
        if not isinstance(label, dict):
            continue

        pre = label.get("pre") or {}
        ask = label.get("ask") or {}
        post = label.get("post") or {}
        pre_tried = _norm_label(pre.get("tried"))
        ask_type = _norm_label(ask.get("type"))
        ask_goal = _norm_label(ask.get("goal"))
        post_mode = _norm_label(post.get("mode"))

        if drop_unk_ask and ask_type == "unk":
            continue

        ts = float(rec.get("timestamp") or math.nan)
        out.append(
            _A1ChatLabel(
                timestamp=ts,
                problem=str(problem),
                pre_tried=pre_tried,
                ask_type=ask_type,
                ask_goal=ask_goal,
                post_mode=post_mode,
            )
        )

    out.sort(key=lambda c: (c.problem, c.timestamp))
    return out


def _attempted_map_python(details_by_user: dict, user_id: str) -> dict[str, bool]:
    rec = details_by_user.get(user_id, {})
    if not isinstance(rec, dict):
        return {}
    probs = rec.get("problems", {})
    if not isinstance(probs, dict):
        return {}
    out: dict[str, bool] = {}
    for p, prec in probs.items():
        if not isinstance(prec, dict):
            continue
        out[str(p)] = bool(prec.get("user_answer") is not None)
    return out


def _compute_single_problem_features(
    seq: list[_A1ChatLabel],
    *,
    attempted_without_chat: bool,
    nochat_tried_if_attempted: bool,
) -> dict[str, object]:
    if not seq:
        return {
            "n_chats": 0,
            "tried_any": bool(attempted_without_chat and nochat_tried_if_attempted),
            "mindless_copy": False,
            "any_answer_copy": False,
            "ask_then_explain": False,
        }

    seq = sorted(seq, key=lambda c: c.timestamp)
    tried_any = any(c.pre_tried == LABEL_TRIED_Y for c in seq)

    # Updated mindless-copy definition
    mindless_copy = any(
        (((c.ask_type in FINAL_ANSWER_TYPES) or (c.ask_goal in FINAL_ANSWER_GOALS)) and (c.pre_tried == LABEL_TRIED_N))
        for c in seq
    )

    any_answer_copy = any(
        ((c.ask_type in FINAL_ANSWER_TYPES) or (c.ask_goal in FINAL_ANSWER_GOALS))
        and (c.post_mode in COPYLIKE_MODES)
        for c in seq
    )

    # After an answer request, later asks for explanation/concept.
    seen_answer = False
    ask_then_explain = False
    for c in seq:
        is_answer = (c.ask_type in FINAL_ANSWER_TYPES) or (c.ask_goal in FINAL_ANSWER_GOALS)
        is_explain = (c.ask_goal in EXPLAIN_GOALS) or (c.ask_type in EXPLAIN_TYPES)
        if is_answer:
            seen_answer = True
        elif seen_answer and is_explain:
            ask_then_explain = True
            break

    return {
        "n_chats": len(seq),
        "tried_any": bool(tried_any),
        "mindless_copy": bool(mindless_copy),
        "any_answer_copy": bool(any_answer_copy),
        "ask_then_explain": bool(ask_then_explain),
    }


def _pick_a1_category(
    *,
    n_chats: int,
    tried_rate_problem: float,
    mindless_copy_rate_problem: float,
    ask_then_explain: bool,
    tried_threshold: float = TRIED_THRESHOLD,
    copy_first_threshold: float = COPY_FIRST_THRESHOLD,
    precedence: tuple[str, ...] = PRECEDENCE,
) -> str:
    return pick_python_a1_category(
        n_chats=n_chats,
        tried_rate_problem=tried_rate_problem,
        mindless_copy_rate_problem=mindless_copy_rate_problem,
        ask_then_explain=ask_then_explain,
        tried_threshold=tried_threshold,
        copy_first_threshold=copy_first_threshold,
        precedence=precedence,
    )


def compute_python_a1_behavior_groups(
    usernames: list[str],
    *,
    labels_path: Path,
    python_details_path: Path,
    stage: str = "a1",
    problem_prefix: str = "py_",
    drop_unk_ask: bool = True,
    problem_denom_policy: str = "attempted_or_chatted",
    nochat_tried_if_attempted: bool = True,
) -> dict[str, str]:
    """
    Return user_id -> category, using the same logic as analyze/a1_behavior_analyze_py.py.
    """
    labels_by_user = behavior_a1.load_json(labels_path)
    details_by_user = behavior_a1.load_json(python_details_path)
    scores = {uid: {"group": "Experiment"} for uid in usernames}
    target_problems = behavior_a1.infer_target_problems_from_labels(
        labels_by_user,
        stage=stage,
        problem_prefix=problem_prefix,
    )
    user_problem_chats = behavior_a1.build_user_problem_chats(
        labels_by_user,
        scores,
        details_by_user,
        group="Experiment",
        stage=stage,
        problem_prefix=problem_prefix,
        drop_unk_ask=drop_unk_ask,
        target_problems=target_problems,
        problem_denom_policy=problem_denom_policy,
        excluded_users=set(),
    )
    attempted_without_chat = behavior_a1.build_user_problem_attempted_map(user_problem_chats, details_by_user)
    feats_by_user = behavior_a1.compute_all_user_features(
        user_problem_chats,
        attempted_without_chat,
        scores,
        tried_threshold=TRIED_THRESHOLD,
        copy_first_threshold=COPY_FIRST_THRESHOLD,
        precedence=behavior_a1.PYTHON_A1_PRECEDENCE,
        nochat_tried_if_attempted=nochat_tried_if_attempted,
    )
    return {uid: feat.category for uid, feat in feats_by_user.items()}


def _iter_user_math_chat_labels(
    labels_by_user: dict,
    user_id: str,
    *,
    stage: str,
    problem_prefix: str,
    drop_unk_ask: bool,
) -> list[_MathChatLabel]:
    user_blob = labels_by_user.get(user_id, {})
    if not isinstance(user_blob, dict) or not user_blob:
        return []

    out: list[_MathChatLabel] = []
    for _action_id, rec in user_blob.items():
        if not isinstance(rec, dict):
            continue
        if stage and rec.get("stage") != stage:
            continue
        action = rec.get("action", "")
        if not (isinstance(action, str) and action.endswith("::chat")):
            continue
        problem = rec.get("problem") or (action.split("::", 1)[0] if "::" in action else action)
        if not (isinstance(problem, str) and problem.startswith(problem_prefix)):
            continue

        label = rec.get("label") or {}
        pre_tried = str(_safe_get(label, ("pre", "tried"), default="unk"))
        ask_type = str(_safe_get(label, ("ask", "type"), default="unk"))
        ask_goal = str(_safe_get(label, ("ask", "goal"), default="unk"))
        post_mode = str(_safe_get(label, ("post", "mode"), default="unk"))
        pre_blanks = _safe_get(label, ("pre", "blanks"), default={}) or {}
        ask_blanks = _safe_get(label, ("ask", "blanks"), default={}) or {}
        post_blanks = _safe_get(label, ("post", "blanks"), default={}) or {}
        llm_wrong = _blanks_any_correct(ask_blanks, want_correct=False)
        post_has_correct = _blanks_any_correct(post_blanks, want_correct=True)

        if drop_unk_ask and ask_type == "unk":
            continue

        try:
            ts_f = float(rec.get("timestamp"))
        except Exception:
            ts_f = float("nan")

        out.append(
            _MathChatLabel(
                timestamp=ts_f,
                problem=str(problem),
                pre_tried=pre_tried,
                ask_type=ask_type,
                ask_goal=ask_goal,
                post_mode=post_mode,
                llm_wrong=bool(llm_wrong),
                post_has_correct=bool(post_has_correct),
                ask_blanks=ask_blanks if isinstance(ask_blanks, dict) else {},
                post_blanks=post_blanks if isinstance(post_blanks, dict) else {},
                pre_blanks=pre_blanks if isinstance(pre_blanks, dict) else {},
            )
        )

    out.sort(key=lambda c: (c.problem, c.timestamp))
    return out


def _compute_single_problem_features_math(
    seq: list[_MathChatLabel],
    *,
    problem_id: str,
    attempted_without_chat: bool,
    nochat_tried_if_attempted: bool,
    pretry_blank_prop_threshold: float,
) -> dict[str, object]:
    if not seq:
        return {
            "n_chats": 0,
            "tried_any": bool(attempted_without_chat and nochat_tried_if_attempted),
            "mindless_copy": False,
            "any_answer_copy": False,
            "ask_then_explain": False,
            "eligible_for_rates": True,
        }

    seq = sorted(seq, key=lambda c: c.timestamp)
    any_answer_request = any(
        ((c.ask_type in FINAL_ANSWER_TYPES) or (c.ask_goal in FINAL_ANSWER_GOALS)) for c in seq
    )
    pretry_rate = _pretry_rate_for_problem(problem_id, seq)
    if not any_answer_request:
        tried_any = True
    elif pretry_rate is None:
        tried_any = any(c.pre_tried == LABEL_TRIED_Y for c in seq)
    else:
        tried_any = pretry_rate >= pretry_blank_prop_threshold
    any_post_verbatim = any(c.post_mode in MATH_VERBATIM_MODES for c in seq)

    seen_answer = False
    ask_then_explain = False
    for c in seq:
        is_explain = (c.ask_goal in EXPLAIN_GOALS)
        is_answer = ((c.ask_type in FINAL_ANSWER_TYPES) or (c.ask_goal in FINAL_ANSWER_GOALS)) and (not is_explain)
        if is_explain:
            if seen_answer:
                ask_then_explain = True
                break
        elif is_answer:
            seen_answer = True

    all_post_none = all(c.post_mode == "none" for c in seq)
    any_post_blank = any(isinstance(c.post_blanks, dict) and len(c.post_blanks) > 0 for c in seq)
    no_time_problem = all_post_none and (not any_post_blank) and (not attempted_without_chat)
    eligible_for_rates = not no_time_problem

    mindless_copy = bool((not tried_any) and any_answer_request and any_post_verbatim and eligible_for_rates)

    any_answer_copy = any(
        ((c.ask_type in FINAL_ANSWER_TYPES) or (c.ask_goal in FINAL_ANSWER_GOALS))
        and (c.post_mode in COPYLIKE_MODES)
        for c in seq
    )

    return {
        "n_chats": len(seq),
        "tried_any": bool(tried_any),
        "mindless_copy": bool(mindless_copy),
        "any_answer_copy": bool(any_answer_copy),
        "ask_then_explain": bool(ask_then_explain),
        "eligible_for_rates": bool(eligible_for_rates),
    }


def _pick_math_category(
    *,
    n_chats: int,
    tried_rate_problem: float,
    mindless_copy_rate_problem: float,
    ask_then_explain: bool,
    challenge_wrong: bool,
    fix_after_wrong: bool,
    tried_threshold: float = MATH_TRIED_THRESHOLD,
    copy_first_threshold: float = MATH_COPY_FIRST_THRESHOLD,
    precedence: tuple[str, ...] = MATH_PRECEDENCE,
) -> str:
    return pick_math_a1_category(
        n_chats=n_chats,
        tried_rate_problem=tried_rate_problem,
        mindless_copy_rate_problem=mindless_copy_rate_problem,
        ask_then_explain=ask_then_explain,
        challenge_wrong=challenge_wrong,
        fix_after_wrong=fix_after_wrong,
        tried_threshold=tried_threshold,
        copy_first_threshold=copy_first_threshold,
        precedence=precedence,
    )


def compute_math_a1_behavior_groups(
    usernames: list[str],
    *,
    labels_path: Path,
    math_details_path: Path,
    stage: str = "a1",
    problem_prefix: str = "math_",
    drop_unk_ask: bool = True,
    problem_denom_policy: str = "attempted_or_chatted",
    nochat_tried_if_attempted: bool = True,
    pretry_blank_prop_threshold: float = MATH_PRETRY_BLANK_PROP_THRESHOLD,
) -> dict[str, str]:
    """
    Return user_id -> category, using the same logic as analyze/a1_behavior_analyze_math.py.
    """
    labels_by_user = behavior_a1.load_json(labels_path)
    details_by_user = behavior_a1.load_json(math_details_path)
    scores = {uid: {"group": "Experiment"} for uid in usernames}
    target_problems = behavior_a1.infer_target_problems_from_labels(
        labels_by_user,
        stage=stage,
        problem_prefix=problem_prefix,
    )
    old_threshold = behavior_a1._compute_single_problem_features_math.__globals__["PRETRY_BLANK_PROP_THRESHOLD"]
    behavior_a1._compute_single_problem_features_math.__globals__[
        "PRETRY_BLANK_PROP_THRESHOLD"
    ] = pretry_blank_prop_threshold
    try:
        user_problem_chats = behavior_a1.build_user_problem_chats_math(
            labels_by_user,
            scores,
            details_by_user,
            group="Experiment",
            stage=stage,
            problem_prefix=problem_prefix,
            drop_unk_ask=drop_unk_ask,
            target_problems=target_problems,
            problem_denom_policy=problem_denom_policy,
            excluded_users=set(),
        )
        attempted_without_chat = behavior_a1.build_user_problem_attempted_map_math(user_problem_chats, details_by_user)
        feats_by_user = behavior_a1.compute_all_user_features_math(
            user_problem_chats,
            attempted_without_chat,
            scores,
            tried_threshold=MATH_TRIED_THRESHOLD,
            copy_first_threshold=MATH_COPY_FIRST_THRESHOLD,
            precedence=behavior_a1.MATH_A1_PRECEDENCE,
            nochat_tried_if_attempted=nochat_tried_if_attempted,
        )
    finally:
        behavior_a1._compute_single_problem_features_math.__globals__[
            "PRETRY_BLANK_PROP_THRESHOLD"
        ] = old_threshold
    return {uid: feat.category for uid, feat in feats_by_user.items()}


def _stacked_bar_proportion_plot(
    ax,
    prop_df: pd.DataFrame,
    *,
    title: str,
    colors: dict[str, str],
    xlabel: Optional[str] = None,
) -> None:
    if prop_df.empty:
        ax.text(0.5, 0.5, "No data available", ha="center", va="center", transform=ax.transAxes)
        ax.set_title(title)
        return

    x = np.arange(len(prop_df.index))
    bottom = np.zeros(len(prop_df.index), dtype=float)
    for col in prop_df.columns:
        ys = prop_df[col].values.astype(float)
        ax.bar(
            x,
            ys,
            bottom=bottom,
            label=col,
            color=colors.get(col, "#9CA3AF"),
            edgecolor="white",
            linewidth=0.6,
        )
        bottom += ys

    ax.set_xticks(x)
    xticklabels = ["Medium" if str(v) == "Mid" else str(v) for v in list(prop_df.index)]
    ax.set_xticklabels(xticklabels, rotation=0)
    ax.set_ylim(0, 1)
    ax.set_title(title, pad=10)
    ax.set_ylabel("Share of participants")
    if xlabel:
        ax.set_xlabel(xlabel)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle=":", alpha=0.25, color="#CCCCCC")


def plot_python_a1_behavior_group_proportions(
    python_df: pd.DataFrame, output_file: Path, *, show: bool = True
) -> None:
    labels_path = REPO_ROOT / "data/annotation/a1_chat_labels.json"
    python_details_path = REPO_ROOT / "data/annotation/python_details.json"

    df_exp = python_df[python_df["group"] == 1].copy()
    if df_exp.empty:
        print("[A1 behavior] No Python Experiment users found; skip behavior plots.")
        return

    if "university_cat" not in df_exp.columns:
        df_exp["university_cat"] = df_exp["university_ranking_num"].apply(normalize_university_ranking_from_num)
    if "capability_cat" not in df_exp.columns:
        df_exp["capability_cat"] = df_exp["captest_score"].apply(lambda x: categorize_capability_from_score(x, "python"))

    user_ids = sorted(df_exp["username"].dropna().astype(str).unique().tolist())
    user_to_cat = compute_python_a1_behavior_groups(
        user_ids,
        labels_path=labels_path,
        python_details_path=python_details_path,
        stage="a1",
        problem_prefix="py_",
        drop_unk_ask=True,
        problem_denom_policy="attempted_or_chatted",
        nochat_tried_if_attempted=True,
    )
    df_exp["a1_behavior_group"] = df_exp["username"].map(user_to_cat).fillna("no_chat")

    behavior_order = list(PYTHON_A1_DISPLAY_ORDER)
    display_name = PYTHON_A1_DISPLAY_NAMES
    direction_by_group = {
        display_name["no_chat"]: "less",
        display_name["mindless_copy"]: "less",
        display_name["try_then_ask"]: "greater",
        display_name["ask_then_explain"]: "greater",
    }
    colors = {
        "Abstention": "#c6dbef",
        "Rote-adoption": "#9ecae1",
        "Active-trial": "#a1d99b",
        "Verification": "#31a354",
    }

    dims = [
        ("university_cat", ["Low", "Mid", "High"], "University ranking"),
        ("capability_cat", ["Low", "Mid", "High"], "Prior knowledge"),
    ]

    prop_tables: list[pd.DataFrame] = []
    for col, order, _title in dims:
        sub = df_exp[[col, "a1_behavior_group"]].dropna().copy()
        sub[col] = pd.Categorical(sub[col], categories=order, ordered=True)
        sub = sub[sub[col].notna()].copy()

        counts = (
            sub.groupby([col, "a1_behavior_group"], observed=False)
            .size()
            .unstack(fill_value=0)
            .reindex(index=order, fill_value=0)
        )
        for b in behavior_order:
            if b not in counts.columns:
                counts[b] = 0
        counts = counts[behavior_order]

        denom = counts.sum(axis=1).replace(0, np.nan)
        props = counts.div(denom, axis=0).fillna(0.0)
        props = props.rename(columns={k: display_name[k] for k in behavior_order})
        prop_tables.append(props)

    _set_nature_style_like_a1_behavior_analyze()
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.6), dpi=300, constrained_layout=False)
    for ax, (_col, _order, xlabel), props in zip(axes, dims, prop_tables):
        _stacked_bar_proportion_plot(ax, props, title="", colors=colors, xlabel=xlabel)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.90])
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.985),
        ncol=4,
        frameon=False,
        fontsize=12,
    )
    for ax in axes:
        if ax.get_legend() is not None:
            ax.get_legend().remove()

    output_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_file, bbox_inches="tight", dpi=300)
    if show:
        plt.show()
    plt.close(fig)
    print(f"[A1 behavior] Saved behavior-group proportions plot to: {relative_path(output_file)}")


def plot_math_a1_behavior_group_proportions(
    math_df: pd.DataFrame, output_file: Path, *, show: bool = True
) -> None:
    labels_path = REPO_ROOT / "data/annotation/a1_chat_labels.json"
    math_details_path = REPO_ROOT / "data/annotation/math_score_reviews_with_answers.json"

    df_exp = math_df[math_df["group"] == 1].copy()
    if df_exp.empty:
        print("[A1 behavior] No Math Experiment users found; skip behavior plots.")
        return

    if "university_cat" not in df_exp.columns:
        df_exp["university_cat"] = df_exp["university_ranking_num"].apply(normalize_university_ranking_from_num)
    if "capability_cat" not in df_exp.columns:
        df_exp["capability_cat"] = df_exp["captest_score"].apply(lambda x: categorize_capability_from_score(x, "math"))

    user_ids = sorted(df_exp["username"].dropna().astype(str).unique().tolist())
    user_to_cat = compute_math_a1_behavior_groups(
        user_ids,
        labels_path=labels_path,
        math_details_path=math_details_path,
        stage="a1",
        problem_prefix="math_",
        drop_unk_ask=True,
        problem_denom_policy="attempted_or_chatted",
        nochat_tried_if_attempted=True,
    )
    df_exp["a1_behavior_group"] = df_exp["username"].map(user_to_cat).fillna("no_chat")

    behavior_order = list(MATH_A1_DISPLAY_ORDER)
    display_name = MATH_A1_DISPLAY_NAMES
    colors = {
        "Abstention": "#c6dbef",
        "Rote-adoption": "#9ecae1",
        "Active-trial": "#a1d99b",
        "Verification": "#238b45",
        "Error-correction": "#74c476",
    }

    dims = [
        ("university_cat", ["Low", "Mid", "High"], "University ranking"),
        ("capability_cat", ["Low", "Mid", "High"], "Prior knowledge"),
    ]

    prop_tables: list[pd.DataFrame] = []
    for col, order, _title in dims:
        sub = df_exp[[col, "a1_behavior_group"]].dropna().copy()
        sub[col] = pd.Categorical(sub[col], categories=order, ordered=True)
        sub = sub[sub[col].notna()].copy()

        counts = (
            sub.groupby([col, "a1_behavior_group"], observed=False)
            .size()
            .unstack(fill_value=0)
            .reindex(index=order, fill_value=0)
        )
        for b in behavior_order:
            if b not in counts.columns:
                counts[b] = 0
        counts["Verification"] = counts["challenge_wrong"] + counts["ask_then_explain"]
        counts = counts[["no_chat", "mindless_copy", "try_then_ask", "fix_after_wrong", "Verification"]]

        denom = counts.sum(axis=1).replace(0, np.nan)
        props = counts.div(denom, axis=0).fillna(0.0)
        props = props.rename(
            columns={
                "no_chat": display_name["no_chat"],
                "mindless_copy": display_name["mindless_copy"],
                "try_then_ask": display_name["try_then_ask"],
                "fix_after_wrong": display_name["fix_after_wrong"],
                "Verification": "Verification",
            }
        )
        prop_tables.append(props)

    _set_nature_style_like_a1_behavior_analyze()
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 3.6), dpi=300, constrained_layout=False)
    for ax, (_col, _order, xlabel), props in zip(axes, dims, prop_tables):
        _stacked_bar_proportion_plot(ax, props, title="", colors=colors, xlabel=xlabel)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.90])
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.02),
        ncol=3,
        frameon=False,
        fontsize=12,
    )
    for ax in axes:
        if ax.get_legend() is not None:
            ax.get_legend().remove()

    output_file.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_file, bbox_inches="tight", dpi=300)
    if show:
        plt.show()
    plt.close(fig)
    print(f"[A1 behavior] Saved behavior-group proportions plot to: {relative_path(output_file)}")


def calculate_means_by_category(
    df,
    category_col,
    outcome_col,
    group_col="group",
):
    def _bootstrap_mean_ci(values: pd.Series, *, seed: int, n_boot: int = 5000) -> tuple[float, float, float]:
        data = values.dropna().to_numpy(dtype=float)
        if data.size == 0:
            return float("nan"), float("nan"), float("nan")
        mean = float(np.mean(data))
        if data.size == 1:
            return mean, mean, mean
        rng = np.random.default_rng(seed)
        samples = rng.choice(data, size=(n_boot, data.size), replace=True).mean(axis=1)
        low, high = np.percentile(samples, [2.5, 97.5])
        return mean, float(low), float(high)

    results = []

    unique_categories = df[category_col].dropna().unique()
    try:
        unique_categories = sorted(unique_categories)
    except Exception:
        unique_categories = sorted(unique_categories, key=str)

    category_seed_order = {"Low": 0, "Mid": 1, "High": 2}
    for cat_idx, category in enumerate(unique_categories):
        seed_idx = category_seed_order.get(str(category), cat_idx)
        cat_df = df[df[category_col] == category]

        row_data = {category_col: category}

        for group_val, group_name in [(0, "Control"), (1, "Treatment")]:
            group_df = cat_df[cat_df[group_col] == group_val]

            if len(group_df) > 0:
                valid_data = group_df[[outcome_col]].dropna()
                if len(valid_data) > 0:
                    mean_val, ci_low, ci_high = _bootstrap_mean_ci(
                        valid_data[outcome_col],
                        seed=20260616 + seed_idx * 10 + int(group_val),
                    )
                    count = len(valid_data)
                else:
                    mean_val = np.nan
                    ci_low = np.nan
                    ci_high = np.nan
                    count = 0
            else:
                mean_val = np.nan
                ci_low = np.nan
                ci_high = np.nan
                count = 0

            row_data[f"{group_name}_Mean"] = mean_val
            row_data[f"{group_name}_CI_Low"] = ci_low
            row_data[f"{group_name}_CI_High"] = ci_high
            row_data[f"{group_name}_N"] = count

        results.append(row_data)

    res_df = pd.DataFrame(results)
    res_df["Gap"] = res_df["Treatment_Mean"] - res_df["Control_Mean"]

    return res_df


def normalize_university_ranking_from_num(value):
    if pd.isna(value) or value == 0:
        return None
    if value >= 4:
        return "High"
    if value >= 2:
        return "Mid"
    return "Low"


def categorize_capability_from_score(score, course_type):
    if pd.isna(score):
        return None

    if course_type == "python":
        if score < 3:
            return "Low"
        if score <= 6.5:
            return "Mid"
        return "High"
    
    # Temporary unified thresholds for both courses
    if score <= 3.5:
        return "Low"
    if score <= 6.5:
        return "Mid"
    return "High"


def plot_dimension_subplot(
    ax,
    stats_df,
    category_col,
    category_order,
    *,
    raw_df: pd.DataFrame,
    outcome_col: str = "hw2_score",
    y_label: str = "Exam score",
    annotation: str = "interaction",
    title: str = "",
    xlabel: Optional[str] = None,
    y_limits: Optional[Tuple[float, float]] = None,
    diff_max_abs: Optional[float] = None,
    plot_style=None,
):
    if plot_style is None:
        plot_style = {}
    stats_filtered = stats_df[stats_df[category_col].isin(category_order)].copy()
    stats_filtered[category_col] = pd.Categorical(
        stats_filtered[category_col],
        categories=category_order,
        ordered=True,
    )
    stats_filtered = stats_filtered.sort_values(category_col)

    if len(stats_filtered) == 0:
        ax.text(0.5, 0.5, "No data available", ha="center", va="center", transform=ax.transAxes)
        ax.set_title(title, fontsize=plot_style["fontsize_title"])
        return

    x_values = np.arange(len(stats_filtered), dtype=float)
    offsets = {0: -0.08, 1: 0.08}

    def _yerr(group_name: str) -> Optional[np.ndarray]:
        low_col = f"{group_name}_CI_Low"
        high_col = f"{group_name}_CI_High"
        mean_col = f"{group_name}_Mean"
        if low_col not in stats_filtered.columns or high_col not in stats_filtered.columns:
            return None
        means = stats_filtered[mean_col].to_numpy(dtype=float)
        lows = stats_filtered[low_col].to_numpy(dtype=float)
        highs = stats_filtered[high_col].to_numpy(dtype=float)
        return np.vstack([means - lows, highs - means])

    ax.errorbar(
        x_values + offsets[0],
        stats_filtered["Control_Mean"].to_numpy(dtype=float),
        yerr=_yerr("Control"),
        marker="o",
        linestyle="-",
        color=CONTROL_COLOR,
        markersize=plot_style["marker_size"],
        alpha=plot_style["alpha"],
        linewidth=plot_style["linewidth"],
        elinewidth=plot_style.get("errorbar_linewidth", 1.0),
        capsize=plot_style.get("errorbar_capsize", 3.0),
        label="Control",
        zorder=3,
    )
    ax.errorbar(
        x_values + offsets[1],
        stats_filtered["Treatment_Mean"].to_numpy(dtype=float),
        yerr=_yerr("Treatment"),
        marker="s",
        linestyle="--",
        color=EXPERIMENT_COLOR,
        markersize=plot_style["marker_size"],
        alpha=plot_style["alpha"],
        linewidth=plot_style["linewidth"],
        elinewidth=plot_style.get("errorbar_linewidth", 1.0),
        capsize=plot_style.get("errorbar_capsize", 3.0),
        label="Treatment",
        zorder=3,
    )

    ax.set_xticks(x_values)
    xticklabels = [
        "Medium" if str(v) == "Mid" else str(v)
        for v in stats_filtered[category_col]
    ]
    ax.set_xticklabels(xticklabels, rotation=0, ha="center")
    if title:
        ax.set_title(title, fontsize=plot_style["fontsize_title"])
    ax.set_xlabel(xlabel or "", fontsize=plot_style["fontsize_label"])
    ax.set_ylabel(y_label, fontsize=plot_style["fontsize_label"])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(
        axis="both",
        which="both",
        length=4,
        width=1,
        labelsize=plot_style["fontsize_tick"],
    )
    ax.grid(False)
    if y_limits is not None:
        ax.set_ylim(y_limits[0], y_limits[1])
    else:
        ax.set_ylim(bottom=0)

    diffs = (stats_filtered["Treatment_Mean"] - stats_filtered["Control_Mean"]).values.astype(float)
    if len(diffs) > 0:
        ax2 = ax.twinx()
        ax2.set_zorder(0)
        ax.set_zorder(1)
        ax.patch.set_visible(False)
        pos_color = plot_style["diff_pos_color"]
        neg_color = plot_style["diff_neg_color"]
        bar_colors = [pos_color if d >= 0 else neg_color for d in diffs]
        ax2.bar(
            x_values,
            diffs,
            width=0.36,
            color=bar_colors,
            alpha=plot_style["diff_alpha"],
            zorder=0,
        )
        if diff_max_abs is None:
            max_abs = float(np.max(np.abs(diffs))) if len(diffs) else 0.0
            max_abs = max(max_abs, 0.2)
        else:
            max_abs = max(float(diff_max_abs), 0.2)
        ax2.set_ylim(-1.2 * max_abs, 1.2 * max_abs)
        ax2.set_yticks([])
        ax2.spines["top"].set_visible(False)
        ax2.spines["right"].set_visible(False)
        ax2.spines["left"].set_visible(False)
        for x_pos, d, c in zip(x_values, diffs, bar_colors):
            ax.text(
                x_pos,
                0.055,
                f"{d:+.2f}",
                transform=ax.get_xaxis_transform(),
                ha="center",
                va="bottom",
                fontsize=plot_style["fontsize_diff"],
                color=c,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.72, "pad": 0.6},
                zorder=5,
            )

    if annotation != "interaction":
        return

    # Interaction coefficient annotation (Experiment vs Control, 3-bin numeric)
    def _interaction_coef_binned(df: pd.DataFrame, *, cat_key: str, y_key: str) -> float | None:
        if df.empty or df["group"].nunique() < 2:
            return None
        order = ["Low", "Mid", "High"]
        sub = df[[cat_key, "group", y_key]].dropna().copy()
        sub[cat_key] = pd.Categorical(sub[cat_key].astype(str), categories=order, ordered=True)
        sub = sub[sub[cat_key].notna()]
        if sub.empty:
            return None
        sub["bin_num"] = sub[cat_key].cat.codes.astype(float) + 1.0
        formula = f"{y_key} ~ bin_num + group + bin_num:group"
        try:
            model = smf.ols(formula, data=sub).fit()
        except Exception:
            return None
        coef = model.params.get("bin_num:group", float("nan"))
        if math.isnan(coef):
            coef = model.params.get("group:bin_num", float("nan"))
        if math.isnan(coef):
            return None
        return float(coef)

    sub = raw_df[[category_col, outcome_col, "group"]].dropna().copy()
    sub = sub[sub["group"].isin([0, 1])]
    a3 = _interaction_coef_binned(sub, cat_key=category_col, y_key=outcome_col)
    if a3 is not None:
        ax.text(
            0.5,
            0.96,
            rf"$\beta_3={a3:+.2f}$",
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=10,
            color="black",
        )


def plot_equity_assignment_scores(
    python_df,
    math_df,
    output_file,
    *,
    outcome_col: str,
    y_label: str,
    annotation: str = "interaction",
    capability_categorizer=categorize_capability_from_score,
    report_interaction_stats: bool = False,
    show: bool = True,
):
    print(f"\nGenerating unweighted equity analysis plot for {outcome_col}...")

    python_df["university_cat"] = python_df["university_ranking_num"].apply(
        normalize_university_ranking_from_num
    )
    python_df["capability_cat"] = python_df["captest_score"].apply(
        lambda x: capability_categorizer(x, "python")
    )

    math_df["university_cat"] = math_df["university_ranking_num"].apply(
        normalize_university_ranking_from_num
    )
    math_df["capability_cat"] = math_df["captest_score"].apply(
        lambda x: capability_categorizer(x, "math")
    )

    if report_interaction_stats:
        print(f"\nInteraction tests ({y_label.lower()}, unweighted)...")
        _run_binned_numeric_model(
            python_df,
            "university_cat",
            "Python University rank",
            outcome_col=outcome_col,
        )
        _run_binned_numeric_model(
            python_df,
            "capability_cat",
            "Python Prior knowledge",
            outcome_col=outcome_col,
        )
        _run_binned_numeric_model(
            math_df,
            "university_cat",
            "Game Theory University rank",
            outcome_col=outcome_col,
        )
        _run_binned_numeric_model(
            math_df,
            "capability_cat",
            "Game Theory Prior knowledge",
            outcome_col=outcome_col,
        )

    dimensions = [
        {
            "col": "university_cat",
            "order": ["Low", "Mid", "High"],
            "title": "",
            "xlabel": "University ranking",
        },
        {
            "col": "capability_cat",
            "order": ["Low", "Mid", "High"],
            "title": "",
            "xlabel": "Prior knowledge",
        },
    ]

    course_stats = {"Python": {}, "Math": {}}

    for dim in dimensions:
        course_stats["Python"][dim["col"]] = calculate_means_by_category(
            df=python_df,
            category_col=dim["col"],
            outcome_col=outcome_col,
        )
        course_stats["Math"][dim["col"]] = calculate_means_by_category(
            df=math_df,
            category_col=dim["col"],
            outcome_col=outcome_col,
        )

    all_means = []
    all_diffs = []
    for course_name in ["Python", "Math"]:
        for dim in dimensions:
            stats_df = course_stats[course_name][dim["col"]]
            if "Control_Mean" in stats_df.columns:
                all_means.extend([v for v in stats_df["Control_Mean"].tolist() if pd.notna(v)])
            if "Treatment_Mean" in stats_df.columns:
                all_means.extend([v for v in stats_df["Treatment_Mean"].tolist() if pd.notna(v)])
            for ci_col in [
                "Control_CI_Low",
                "Control_CI_High",
                "Treatment_CI_Low",
                "Treatment_CI_High",
            ]:
                if ci_col in stats_df.columns:
                    all_means.extend([v for v in stats_df[ci_col].tolist() if pd.notna(v)])
            if "Gap" in stats_df.columns:
                all_diffs.extend([v for v in stats_df["Gap"].tolist() if pd.notna(v)])

    if all_means:
        y_max = float(max(all_means))
        y_max = max(0.0, y_max)
        y_min = float(min(all_means))
        y_lower = min(-0.35, y_min - 0.03 * max(y_max - y_min, 1.0))
        y_limits = (y_lower, y_max * 1.08 if y_max > 0 else 1.0)
    else:
        y_limits = (-0.35, 1.0)

    diff_max_abs = float(max([abs(v) for v in all_diffs], default=0.0))

    def _course_y_limits(course_name: str) -> tuple[float, float]:
        vals = []
        for dim in dimensions:
            stats_df = course_stats[course_name][dim["col"]]
            for value_col in [
                "Control_Mean",
                "Treatment_Mean",
                "Control_CI_Low",
                "Control_CI_High",
                "Treatment_CI_Low",
                "Treatment_CI_High",
            ]:
                if value_col in stats_df.columns:
                    vals.extend([v for v in stats_df[value_col].tolist() if pd.notna(v)])
        if not vals:
            return (-0.35, 1.0)
        local_max = max(0.0, float(max(vals)))
        local_min = float(min(vals))
        local_lower = min(-0.35, local_min - 0.03 * max(local_max - local_min, 1.0))
        return (local_lower, local_max * 1.08 if local_max > 0 else 1.0)

    print("\nMean Statistics:")
    for course_name in ["Python", "Math"]:
        print(f"\n{course_name} Course:")
        for dim in dimensions:
            print(f"\n  {dim['title']}:")
            stats_df = course_stats[course_name][dim["col"]]
            print(stats_df.to_string(index=False))

    _set_nature_style_v2()

    plot_style = {
        "fontsize_title": 16,
        "fontsize_label": 15,
        "fontsize_tick": 14,
        "fontsize_diff": 12,
        "linewidth": 1.5,
        "marker_size": 6,
        "alpha": 0.8,
        "errorbar_linewidth": 1.0,
        "errorbar_capsize": 3.0,
        "diff_pos_color": "#74C476",
        "diff_neg_color": "#FB6A4A",
        "diff_alpha": 0.18,
    }

    def _build_legend(fig):
        handles = [
            plt.Line2D(
                [0],
                [0],
                marker="o",
                linestyle="-",
                color=CONTROL_COLOR,
                label="Control",
                markersize=6,
                linewidth=plot_style["linewidth"],
            ),
            plt.Line2D(
                [0],
                [0],
                marker="s",
                linestyle="--",
                color=EXPERIMENT_COLOR,
                label="Experimental",
                markersize=6,
                linewidth=plot_style["linewidth"],
            ),
        ]
        handler_map = None
        try:
            from matplotlib.legend_handler import HandlerBase  # type: ignore
            from matplotlib.patches import Rectangle  # type: ignore

            class _DualColorBox(HandlerBase):
                def create_artists(self, legend, orig_handle, x0, y0, width, height, fontsize, trans):
                    try:
                        from matplotlib.colors import to_rgba  # type: ignore

                        pos = to_rgba(plot_style["diff_pos_color"], plot_style["diff_alpha"])
                        neg = to_rgba(plot_style["diff_neg_color"], plot_style["diff_alpha"])
                    except Exception:
                        pos = plot_style["diff_pos_color"]
                        neg = plot_style["diff_neg_color"]
                    left = Rectangle(
                        (x0, y0),
                        width / 2.0,
                        height,
                        facecolor=pos,
                        edgecolor="none",
                        transform=trans,
                    )
                    right = Rectangle(
                        (x0 + width / 2.0, y0),
                        width / 2.0,
                        height,
                        facecolor=neg,
                        edgecolor="none",
                        transform=trans,
                    )
                    return [left, right]

            dual_handle = object()
            handles.append(dual_handle)
            handler_map = {dual_handle: _DualColorBox()}
        except Exception:
            handles.append(
                plt.Line2D(
                    [0],
                    [0],
                    marker="s",
                    color=plot_style["diff_pos_color"],
                    label="Score Difference",
                    markersize=7,
                    linewidth=0,
                )
            )

        fig.legend(
            handles=handles,
            labels=["Control", "Experimental", "Score Difference"],
            loc="upper center",
            bbox_to_anchor=(0.5, 0.98),
            ncol=3,
            frameon=False,
            fontsize=13,
            columnspacing=1.1,
            handlelength=1.8,
            handler_map=handler_map if handler_map is not None else None,
        )

    def _plot_course(course_name: str, output_path: Path):
        fig = plt.figure(figsize=(7.5, 3.6), dpi=300)
        gs = GridSpec(1, len(dimensions), figure=fig, hspace=0.28, wspace=0.22)
        course_y_limits = _course_y_limits(course_name)
        for dim_idx, dimension in enumerate(dimensions):
            ax = fig.add_subplot(gs[0, dim_idx])
            plot_dimension_subplot(
                ax=ax,
                stats_df=course_stats[course_name][dimension["col"]],
                category_col=dimension["col"],
                category_order=dimension["order"],
                raw_df=python_df if course_name == "Python" else math_df,
                outcome_col=outcome_col,
                y_label=y_label,
                annotation=annotation,
                title="",
                xlabel=dimension["xlabel"],
                y_limits=course_y_limits,
                diff_max_abs=None,
                plot_style=plot_style,
            )
        _build_legend(fig)
        fig.tight_layout(rect=[0.04, 0, 1, 0.94])
        fig.savefig(output_path, bbox_inches="tight", dpi=300)
        print(f"\nSaved unweighted plot to: {relative_path(output_path)}")
        if show:
            plt.show()
        plt.close(fig)

    base = Path(output_file)
    py_out = base.with_name(f"{base.stem}_python{base.suffix}")
    math_out = base.with_name(f"{base.stem}_game_theory{base.suffix}")
    _plot_course("Python", py_out)
    _plot_course("Math", math_out)


def plot_equity(python_df, math_df, output_file, *, show: bool = True):
    return plot_equity_assignment_scores(
        python_df,
        math_df,
        output_file,
        outcome_col="hw2_score",
        y_label="Exam score",
        annotation="interaction",
        show=show,
    )


def plot_equity_hw1(python_df, math_df, output_file, *, show: bool = True):
    return plot_equity_assignment_scores(
        python_df,
        math_df,
        output_file,
        outcome_col="hw1_score",
        y_label="Assignment score",
        annotation="interaction",
        capability_categorizer=categorize_capability_from_score,
        report_interaction_stats=True,
        show=show,
    )


def _calculate_means_by_category_two_groups(
    *,
    df: pd.DataFrame,
    category_col: str,
    category_order: list[str],
    outcome_col: str,
    group_a_mask: pd.Series,
    group_b_mask: pd.Series,
    group_a_label: str,
    group_b_label: str,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for cat in category_order:
        cat_df = df[df[category_col] == cat]
        row = {category_col: cat}
        for label, mask in [(group_a_label, group_a_mask), (group_b_label, group_b_mask)]:
            sub = cat_df[mask.loc[cat_df.index]]
            vals = sub[[outcome_col]].dropna()
            row[f"{label}_Mean"] = float(vals[outcome_col].mean()) if len(vals) > 0 else np.nan
            row[f"{label}_N"] = int(len(vals))
        rows.append(row)
    return pd.DataFrame(rows)


def _plot_behavior_vs_exp_lines(
    *,
    df: pd.DataFrame,
    course_name: str,
    behavior_label: str,
    behavior_color: str,
    output_path: Path,
    show: bool,
) -> None:
    df_exp = df[df["group"] == 1].copy()
    if df_exp.empty:
        print(f"[Behavior equity] No Experiment users for {course_name}; skip {behavior_label}.")
        return

    if "university_cat" not in df_exp.columns:
        df_exp["university_cat"] = df_exp["university_ranking_num"].apply(normalize_university_ranking_from_num)
    if "capability_cat" not in df_exp.columns:
        df_exp["capability_cat"] = df_exp["captest_score"].apply(
            lambda x: categorize_capability_from_score(x, course_name.lower())
        )

    dims = [
        ("university_cat", ["Low", "Mid", "High"], "University ranking"),
        ("capability_cat", ["Low", "Mid", "High"], "Prior knowledge"),
    ]

    exp_mask = pd.Series(True, index=df_exp.index)
    behavior_mask = df_exp["behavior_supergroup"] == behavior_label.lower()

    stats_tables = []
    for col, order, _title in dims:
        stats_tables.append(
            _calculate_means_by_category_two_groups(
                df=df_exp,
                category_col=col,
                category_order=order,
                outcome_col="hw2_score",
                group_a_mask=exp_mask,
                group_b_mask=behavior_mask,
                group_a_label="Experiment",
                group_b_label=behavior_label,
            )
        )

    all_means: list[float] = []
    for stats_df in stats_tables:
        for col in ["Experiment_Mean", f"{behavior_label}_Mean"]:
            if col in stats_df.columns:
                all_means.extend([v for v in stats_df[col].tolist() if pd.notna(v)])
    if all_means:
        y_max = max(all_means)
        y_limits = (0.0, y_max * 1.08 if y_max > 0 else 1.0)
    else:
        y_limits = (0.0, 1.0)

    _set_nature_style_v2()
    fig = plt.figure(figsize=(7.5, 3.6), dpi=300)
    gs = GridSpec(1, len(dims), figure=fig, hspace=0.28, wspace=0.22)

    for idx, (dimension, stats_df) in enumerate(zip(dims, stats_tables)):
        col, order, xlabel = dimension
        ax = fig.add_subplot(gs[0, idx])
        x_values = range(len(order))
        ax.plot(
            x_values,
            stats_df["Experiment_Mean"],
            marker="s",
            linestyle="--",
            color=EXPERIMENT_COLOR,
            markersize=6,
            linewidth=1.6,
            alpha=0.85,
            label="Experimental",
            zorder=3,
        )
        ax.plot(
            x_values,
            stats_df[f"{behavior_label}_Mean"],
            marker="o",
            linestyle="-",
            color=behavior_color,
            markersize=6,
            linewidth=1.6,
            alpha=0.85,
            label=behavior_label,
            zorder=3,
        )
        ax.set_xticks(list(x_values))
        xticklabels = ["Medium" if str(v) == "Mid" else str(v) for v in order]
        ax.set_xticklabels(xticklabels, rotation=0, ha="center")
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Exam score")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="both", which="both", length=4, width=1)
        ax.grid(False)
        ax.set_ylim(y_limits[0], y_limits[1])

    fig.legend(
        handles=[
            plt.Line2D([0], [0], marker="s", linestyle="--", color=EXPERIMENT_COLOR, markersize=6, linewidth=1.6),
            plt.Line2D([0], [0], marker="o", linestyle="-", color=behavior_color, markersize=6, linewidth=1.6),
        ],
        labels=["Experimental", behavior_label],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.98),
        ncol=2,
        frameon=False,
        fontsize=12,
    )
    fig.tight_layout(rect=[0.04, 0, 1, 0.92])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight", dpi=300)
    print(f"[Behavior equity] Saved plot to: {relative_path(output_path)}")
    if show:
        plt.show()
    plt.close(fig)


def _plot_behavior_vs_exp_lines_combined(
    *,
    df: pd.DataFrame,
    course_name: str,
    proactive_critical_color: str,
    passive_color: str,
    output_path: Path,
    show: bool,
    behavior_col: str = "behavior_supergroup",
    explained_metrics: Optional[Dict[str, Dict[str, float | Dict[str, int]]]] = None,
    indirect_metrics: Optional[pd.DataFrame] = None,
) -> None:
    df_exp = df[df["group"] == 1].copy()
    if df_exp.empty:
        print(f"[Behavior equity] No Experiment users for {course_name}; skip combined plot.")
        return

    if "university_cat" not in df_exp.columns:
        df_exp["university_cat"] = df_exp["university_ranking_num"].apply(normalize_university_ranking_from_num)
    if "capability_cat" not in df_exp.columns:
        df_exp["capability_cat"] = df_exp["captest_score"].apply(
            lambda x: categorize_capability_from_score(x, course_name.lower())
        )

    dims = [
        ("university_cat", ["Low", "Mid", "High"], "University ranking"),
        ("capability_cat", ["Low", "Mid", "High"], "Prior knowledge"),
    ]

    behavior_order = ["passive", "proactive_critical"]
    behavior_labels = {
        "passive": "Limited\nengagement",
        "proactive_critical": "Proactive\n& critical",
    }
    palette = {"Low": CONTROL_COLOR, "Mid": "#7F7F7F", "High": EXPERIMENT_COLOR}
    linestyles = {"Low": "-", "Mid": "--", "High": "-."}
    markers = {"Low": "o", "Mid": "s", "High": "^"}
    y_axis_top = 11.0 if course_name.lower() == "math" else None

    def _indirect_beta(metric_key: str) -> float | None:
        if indirect_metrics is None or indirect_metrics.empty:
            return None
        profile_label = (
            "University ranking" if metric_key == "university" else "Prior knowledge"
        )
        rows = indirect_metrics.loc[indirect_metrics["profile"] == profile_label]
        if rows.empty or "indirect_ab" not in rows.columns:
            return None
        value = rows.iloc[0]["indirect_ab"]
        if pd.isna(value):
            return None
        return float(value)

    def _plot_df_for(profile_col: str, profile_order: list[str]) -> pd.DataFrame:
        plot_df = df_exp.loc[
            df_exp[behavior_col].isin(behavior_order)
            & df_exp[profile_col].isin(profile_order),
            ["username", "hw2_score", behavior_col, profile_col],
        ].dropna().copy()
        plot_df[behavior_col] = pd.Categorical(
            plot_df[behavior_col], categories=behavior_order, ordered=True
        )
        plot_df[profile_col] = pd.Categorical(
            plot_df[profile_col].astype(str), categories=profile_order, ordered=True
        )
        return plot_df.sort_values([behavior_col, profile_col, "username"])

    _set_nature_style_v2()
    fig, axes = plt.subplots(
        1,
        len(dims),
        figsize=(7.5, 3.6),
        dpi=300,
        sharey=True,
        gridspec_kw={"wspace": 0.22},
    )
    for ax, (_col, order, xlabel) in zip(axes, dims):
        plot_df = _plot_df_for(_col, order)
        if plot_df.empty:
            ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
            ax.set_axis_off()
            continue
        sns.pointplot(
            data=plot_df,
            x=behavior_col,
            y="hw2_score",
            hue=_col,
            order=behavior_order,
            hue_order=order,
            palette=palette,
            estimator="median",
            errorbar=("ci", 95),
            dodge=0.16,
            markers=[markers[p] for p in order],
            linestyles=[linestyles[p] for p in order],
            linewidth=1.7,
            err_kws={"linewidth": 1.0, "alpha": 0.9},
            capsize=0.07,
            n_boot=5000,
            seed=20260616,
            ax=ax,
        )
        for line in ax.lines:
            color = line.get_color()
            line.set_markerfacecolor(color)
            line.set_markeredgecolor(color)
            line.set_markeredgewidth(1.0)
            line.set_markersize(6.0)
            line.set_alpha(0.9)
        ax.set_xticks(range(len(behavior_order)))
        ax.set_xticklabels([behavior_labels[b] for b in behavior_order], rotation=0, ha="center", fontsize=14)
        ax.set_xlabel(xlabel, fontsize=15)
        ax.set_ylabel("Exam score", fontsize=15)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(
            axis="both",
            which="both",
            direction="out",
            length=5.0,
            width=1.2,
            bottom=True,
            left=True,
            labelleft=True,
            labelsize=14,
        )
        ax.grid(False)
        ax.set_xlim(-0.28, len(behavior_order) - 0.72)
        if y_axis_top is not None:
            ax.set_ylim(0.0, y_axis_top)
        metric_key = "university" if _col == "university_cat" else "prior"
        metrics = (explained_metrics or {}).get(metric_key, {})
        accounted_fraction = metrics.get("accounted_fraction")
        indirect_beta = _indirect_beta(metric_key)
        if indirect_beta is None:
            delta_coef = metrics.get("delta_coef")
            if delta_coef is not None:
                indirect_beta = -1.0 * float(delta_coef)
        if accounted_fraction is not None and indirect_beta is not None:
            ax.text(
                0.5,
                0.96,
                rf"$A_{{\beta}}={100.0 * accounted_fraction:.1f}\%$  $I_{{\beta}}={indirect_beta:.2f}$",
                transform=ax.transAxes,
                ha="center",
                va="top",
                fontsize=10,
                color="black",
            )
        if ax.get_legend() is not None:
            ax.get_legend().remove()

    fig.legend(
        handles=[
            plt.Line2D(
                [0],
                [0],
                marker=markers[profile],
                linestyle=linestyles[profile],
                color=palette[profile],
                markerfacecolor=palette[profile],
                markeredgecolor=palette[profile],
                markeredgewidth=1.0,
                markersize=6,
                linewidth=1.7,
                alpha=0.9,
            )
            for profile in ["Low", "Mid", "High"]
        ],
        labels=["Low profile", "Medium profile", "High profile"],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.96),
        ncol=3,
        frameon=False,
        fontsize=12,
        columnspacing=1.2,
        handlelength=1.8,
    )
    fig.tight_layout(rect=[0.04, 0, 1, 0.94])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight", dpi=300)
    print(f"[Behavior equity] Saved combined plot to: {relative_path(output_path)}")
    if show:
        plt.show()
    plt.close(fig)


def add_behavior_supergroup_python(python_df: pd.DataFrame) -> pd.DataFrame:
    labels_path = REPO_ROOT / "data/annotation/a1_chat_labels.json"
    python_details_path = REPO_ROOT / "data/annotation/python_details.json"

    df = python_df.copy()
    df["behavior_supergroup"] = pd.Series(pd.NA, index=df.index, dtype="object")
    df_exp = df[df["group"] == 1].copy()
    if df_exp.empty:
        return df

    user_ids = sorted(df_exp["username"].dropna().astype(str).unique().tolist())
    user_to_cat = compute_python_a1_behavior_groups(
        user_ids,
        labels_path=labels_path,
        python_details_path=python_details_path,
        stage="a1",
        problem_prefix="py_",
        drop_unk_ask=True,
        problem_denom_policy="attempted_or_chatted",
        nochat_tried_if_attempted=True,
    )
    df_exp["a1_behavior_group"] = df_exp["username"].map(user_to_cat).fillna("no_chat")

    df_exp["behavior_supergroup"] = df_exp["a1_behavior_group"].map(
        lambda category: behavior_supergroup(category, course_type="python")
    )
    df.loc[df_exp.index, "behavior_supergroup"] = df_exp["behavior_supergroup"]
    return df


def add_behavior_supergroup_math(math_df: pd.DataFrame) -> pd.DataFrame:
    labels_path = REPO_ROOT / "data/annotation/a1_chat_labels.json"
    math_details_path = REPO_ROOT / "data/annotation/math_score_reviews_with_answers.json"

    df = math_df.copy()
    df["behavior_supergroup"] = pd.Series(pd.NA, index=df.index, dtype="object")
    df_exp = df[df["group"] == 1].copy()
    if df_exp.empty:
        return df

    user_ids = sorted(df_exp["username"].dropna().astype(str).unique().tolist())
    user_to_cat = compute_math_a1_behavior_groups(
        user_ids,
        labels_path=labels_path,
        math_details_path=math_details_path,
        stage="a1",
        problem_prefix="math_",
        drop_unk_ask=True,
        problem_denom_policy="attempted_or_chatted",
        nochat_tried_if_attempted=True,
    )
    df_exp["a1_behavior_group"] = df_exp["username"].map(user_to_cat).fillna("no_chat")

    df_exp["behavior_supergroup"] = df_exp["a1_behavior_group"].map(
        lambda category: behavior_supergroup(category, course_type="math")
    )
    df.loc[df_exp.index, "behavior_supergroup"] = df_exp["behavior_supergroup"]
    return df


def _compute_r2_from_dummies(
    df: pd.DataFrame,
    *,
    outcome_col: str,
    predictor_cols: list[str],
) -> float | None:
    sub = df[predictor_cols + [outcome_col]].dropna().copy()
    if sub.empty:
        return None
    y = sub[outcome_col].astype(float).values
    if len(y) < 3:
        return None
    X = pd.get_dummies(sub[predictor_cols], drop_first=True)
    X.insert(0, "Intercept", 1.0)
    X_mat = X.values.astype(float)
    try:
        coef, *_ = np.linalg.lstsq(X_mat, y, rcond=None)
    except Exception:
        return None
    y_pred = X_mat @ coef
    ss_res = float(np.sum((y - y_pred) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    if ss_tot == 0:
        return None
    return 1.0 - ss_res / ss_tot


def _extract_term_stats(results: object, term_prefix: str) -> Dict[str, Tuple[float, float]]:
    params = getattr(results, "params", {})
    pvalues = getattr(results, "pvalues", {})
    out: Dict[str, Tuple[float, float]] = {}
    for term, coef in params.items():
        if term.startswith(term_prefix):
            pval = float(pvalues.get(term, float("nan")))
            out[term] = (float(coef), pval)
    return out


def _run_binned_numeric_model(
    df: pd.DataFrame,
    cat_col: str,
    label: str,
    *,
    outcome_col: str = "hw2_score",
) -> None:
    sub = df[[outcome_col, "group", cat_col]].dropna().copy()
    sub = sub[sub["group"].isin([0, 1])]
    if sub.empty or sub["group"].nunique() < 2:
        print(f"  {label}: insufficient data; skip.")
        return
    order = ["Low", "Mid", "High"]
    sub[cat_col] = pd.Categorical(sub[cat_col].astype(str), categories=order, ordered=True)
    sub = sub[sub[cat_col].notna()]
    if sub.empty:
        print(f"  {label}: insufficient data; skip.")
        return
    sub["bin_num"] = sub[cat_col].cat.codes.astype(float) + 1.0
    formula = f"{outcome_col} ~ bin_num + group + bin_num:group"
    try:
        model = smf.ols(formula, data=sub).fit()
    except Exception as exc:
        print(f"  {label}: fit failed ({exc})")
        return

    coef = float(model.params.get("bin_num", float("nan")))
    a3 = float(model.params.get("bin_num:group", float("nan")))
    p_a3 = float(model.pvalues.get("bin_num:group", float("nan")))
    if math.isnan(a3):
        a3 = float(model.params.get("group:bin_num", float("nan")))
        p_a3 = float(model.pvalues.get("group:bin_num", float("nan")))

    slope_ctrl = coef
    slope_exp = coef + a3
    print(f"  {label}: slope_control={slope_ctrl:+.4f}, slope_experiment={slope_exp:+.4f}")
    print(f"    interaction a3={a3:+.4f}, p={p_a3:.6g}")


def report_explained_variance_behavior(
    df: pd.DataFrame,
    course_name: str,
    *,
    metrics: Optional[Dict[str, Dict[str, float | Dict[str, int]]]] = None,
) -> None:
    if metrics is None:
        metrics = compute_explained_variance_behavior_metrics(df, course_name)
    if metrics is None:
        return

    print(f"\n[Coefficient shift] {course_name} (Experiment only)")
    print(f"  Numeric encoding: university_cat={metrics['encoding']['university']}, capability_cat={metrics['encoding']['prior']}")
    uni = metrics["university"]
    cap = metrics["prior"]
    if uni["base_r2"] is not None and uni["full_r2"] is not None:
        print(
            f"  University R^2: base={uni['base_r2']:.4f}, full={uni['full_r2']:.4f}, "
            f"ΔR^2={uni['delta_r2']:+.4f}"
        )
    else:
        print("  University R^2: N/A")
    if cap["base_r2"] is not None and cap["full_r2"] is not None:
        print(
            f"  Prior R^2: base={cap['base_r2']:.4f}, full={cap['full_r2']:.4f}, "
            f"ΔR^2={cap['delta_r2']:+.4f}"
        )
    else:
        print("  Prior R^2: N/A")

    def _report_group(label: str, base_terms: Dict[str, Tuple[float, float]], full_terms: Dict[str, Tuple[float, float]]) -> None:
        if not base_terms:
            print(f"  {label}: N/A")
            return
        sig_to_nonsig_count = 0
        nonsig_to_sig_count = 0
        for term in sorted(base_terms.keys()):
            base_coef, base_p = base_terms[term]
            full_coef, full_p = full_terms.get(term, (float("nan"), float("nan")))
            delta = full_coef - base_coef
            accounted_fraction = (
                (base_coef - full_coef) / base_coef
                if not math.isclose(base_coef, 0.0, abs_tol=1e-12)
                else float("nan")
            )
            shrink = abs(full_coef) < abs(base_coef)
            sig_to_nonsig = (base_p < 0.05) and (full_p >= 0.05)
            nonsig_to_sig = (base_p >= 0.05) and (full_p < 0.05)
            if sig_to_nonsig:
                sig_to_nonsig_count += 1
            if nonsig_to_sig:
                nonsig_to_sig_count += 1
            flags = []
            if shrink:
                flags.append("shrink")
            if sig_to_nonsig:
                flags.append("sig->ns")
            if nonsig_to_sig:
                flags.append("ns->sig")
            flag_str = f" [{', '.join(flags)}]" if flags else ""
            accounted_str = (
                f", accounted={(100.0 * accounted_fraction):.1f}%"
                if np.isfinite(accounted_fraction)
                else ", accounted=N/A"
            )
            print(
                f"  {label} {term}: base={base_coef:+.4f} (p={base_p:.3g}), "
                f"full={full_coef:+.4f} (p={full_p:.3g}), "
                f"Δ={delta:+.4f}{accounted_str}{flag_str}"
            )
        print(
            f"  {label} significance shifts: sig->ns={sig_to_nonsig_count}, ns->sig={nonsig_to_sig_count}"
        )

    _report_group("University", uni["base_terms"], uni["full_terms"])
    _report_group("Prior", cap["base_terms"], cap["full_terms"])


def compute_explained_variance_behavior_metrics(
    df: pd.DataFrame, course_name: str
) -> Optional[Dict[str, Dict[str, float | Dict[str, int]]]]:
    df_exp = df[df["group"] == 1].copy()
    if df_exp.empty:
        print(f"[Coefficient shift] No Experiment users for {course_name}; skip.")
        return None

    if "university_cat" not in df_exp.columns:
        df_exp["university_cat"] = df_exp["university_ranking_num"].apply(normalize_university_ranking_from_num)
    if "capability_cat" not in df_exp.columns:
        df_exp["capability_cat"] = df_exp["captest_score"].apply(
            lambda x: categorize_capability_from_score(x, course_name.lower())
        )

    required_cols = ["hw2_score", "university_cat", "capability_cat", "behavior_supergroup"]
    sub = df_exp[required_cols].dropna().copy()
    if sub.empty or len(sub) < 5:
        print(f"[Coefficient shift] Not enough data for {course_name}; skip.")
        return None

    def _order_levels(values: pd.Series) -> List[str]:
        raw = [str(v) for v in values.unique().tolist()]
        preferred = ["Low", "Mid", "High"]
        ordered = [v for v in preferred if v in raw]
        for v in raw:
            if v not in ordered:
                ordered.append(v)
        return ordered

    uni_levels = _order_levels(sub["university_cat"])
    cap_levels = _order_levels(sub["capability_cat"])
    if not uni_levels or not cap_levels:
        print(f"[Coefficient shift] Missing categories for {course_name}; skip.")
        return None

    sub["university_cat"] = pd.Categorical(sub["university_cat"].astype(str), categories=uni_levels, ordered=True)
    sub["capability_cat"] = pd.Categorical(sub["capability_cat"].astype(str), categories=cap_levels, ordered=True)
    sub["behavior_supergroup"] = sub["behavior_supergroup"].astype(str)

    uni_map = {level: idx + 1 for idx, level in enumerate(uni_levels)}
    cap_map = {level: idx + 1 for idx, level in enumerate(cap_levels)}
    sub["university_cat_num"] = sub["university_cat"].map(uni_map).astype(float)
    sub["capability_cat_num"] = sub["capability_cat"].map(cap_map).astype(float)

    try:
        uni_base_model = smf.ols("hw2_score ~ university_cat_num", data=sub).fit()
        uni_full_model = smf.ols("hw2_score ~ university_cat_num + C(behavior_supergroup)", data=sub).fit()
        cap_base_model = smf.ols("hw2_score ~ capability_cat_num", data=sub).fit()
        cap_full_model = smf.ols("hw2_score ~ capability_cat_num + C(behavior_supergroup)", data=sub).fit()
    except Exception as exc:
        print(f"[Coefficient shift] Model fit failed for {course_name}: {exc}")
        return None

    base_uni = _extract_term_stats(uni_base_model, "university_cat_num")
    full_uni = _extract_term_stats(uni_full_model, "university_cat_num")
    base_cap = _extract_term_stats(cap_base_model, "capability_cat_num")
    full_cap = _extract_term_stats(cap_full_model, "capability_cat_num")

    def _extract_delta(models: tuple[object, object], term: str) -> tuple[float | None, float | None, float | None]:
        base_model, full_model = models
        base_coef = float(getattr(base_model, "params", {}).get(term, float("nan")))
        full_coef = float(getattr(full_model, "params", {}).get(term, float("nan")))
        if np.isnan(base_coef) or np.isnan(full_coef):
            return None, None, None
        return base_coef, full_coef, full_coef - base_coef

    def _accounted_fraction(
        base_coef: float | None, full_coef: float | None
    ) -> float | None:
        if (
            base_coef is None
            or full_coef is None
            or math.isclose(base_coef, 0.0, abs_tol=1e-12)
        ):
            return None
        return (base_coef - full_coef) / base_coef

    uni_base_coef, uni_full_coef, uni_delta_coef = _extract_delta(
        (uni_base_model, uni_full_model), "university_cat_num"
    )
    cap_base_coef, cap_full_coef, cap_delta_coef = _extract_delta(
        (cap_base_model, cap_full_model), "capability_cat_num"
    )
    uni_accounted_fraction = _accounted_fraction(uni_base_coef, uni_full_coef)
    cap_accounted_fraction = _accounted_fraction(cap_base_coef, cap_full_coef)

    def _r2_delta(base_model: object, full_model: object) -> tuple[float | None, float | None, float | None]:
        try:
            base_r2 = float(base_model.rsquared)
            full_r2 = float(full_model.rsquared)
            return base_r2, full_r2, full_r2 - base_r2
        except Exception:
            return None, None, None

    uni_base_r2, uni_full_r2, uni_delta_r2 = _r2_delta(uni_base_model, uni_full_model)
    cap_base_r2, cap_full_r2, cap_delta_r2 = _r2_delta(cap_base_model, cap_full_model)

    return {
        "encoding": {"university": uni_map, "prior": cap_map},
        "university": {
            "base_coef": uni_base_coef,
            "full_coef": uni_full_coef,
            "delta_coef": uni_delta_coef,
            "accounted_fraction": uni_accounted_fraction,
            "base_r2": uni_base_r2,
            "full_r2": uni_full_r2,
            "delta_r2": uni_delta_r2,
            "base_terms": base_uni,
            "full_terms": full_uni,
        },
        "prior": {
            "base_coef": cap_base_coef,
            "full_coef": cap_full_coef,
            "delta_coef": cap_delta_coef,
            "accounted_fraction": cap_accounted_fraction,
            "base_r2": cap_base_r2,
            "full_r2": cap_full_r2,
            "delta_r2": cap_delta_r2,
            "base_terms": base_cap,
            "full_terms": full_cap,
        },
    }


def compute_bootstrap_indirect_association_metrics(
    df: pd.DataFrame,
    course_name: str,
    *,
    n_boot: int = 5000,
    seed: int = 42,
    controls: Optional[List[str]] = None,
) -> Optional[pd.DataFrame]:
    """Estimate indirect associations (a*b) with percentile bootstrap CIs.

    The analysis is restricted to experimental participants. Background strata
    are encoded Low=1, Mid=2, High=3, and the binary mediator is one for the
    proactive-and-critical supergroup.
    """
    if n_boot < 1:
        raise ValueError("n_boot must be at least 1.")

    controls = list(controls or [])
    missing_controls = [col for col in controls if col not in df.columns]
    if missing_controls:
        raise KeyError(f"Missing mediation controls: {missing_controls}")

    df_exp = df[df["group"] == 1].copy()
    if df_exp.empty:
        print(f"[Bootstrap mediation] No Experiment users for {course_name}; skip.")
        return None

    if "university_cat" not in df_exp.columns:
        df_exp["university_cat"] = df_exp["university_ranking_num"].apply(
            normalize_university_ranking_from_num
        )
    if "capability_cat" not in df_exp.columns:
        df_exp["capability_cat"] = df_exp["captest_score"].apply(
            lambda x: categorize_capability_from_score(x, course_name.lower())
        )

    required_cols = [
        "hw2_score",
        "university_cat",
        "capability_cat",
        "behavior_supergroup",
        *controls,
    ]
    sub = df_exp[required_cols].dropna().copy()
    if len(sub) < 5:
        print(f"[Bootstrap mediation] Not enough data for {course_name}; skip.")
        return None

    ordinal_map = {"Low": 1.0, "Mid": 2.0, "High": 3.0}
    sub["university_cat_num"] = sub["university_cat"].astype(str).map(ordinal_map)
    sub["capability_cat_num"] = sub["capability_cat"].astype(str).map(ordinal_map)
    sub["proactive_critical"] = (
        sub["behavior_supergroup"].astype(str) == "proactive_critical"
    ).astype(float)

    rows: List[Dict[str, Any]] = []
    rng = np.random.default_rng(seed)
    specifications = [
        ("University ranking", "university_cat_num"),
        ("Prior knowledge", "capability_cat_num"),
    ]

    for profile_label, x_col in specifications:
        model_cols = ["hw2_score", x_col, "proactive_critical", *controls]
        model_data = sub[model_cols].dropna().astype(float)
        n = len(model_data)
        if (
            n < 5
            or model_data[x_col].nunique() < 2
            or model_data["proactive_critical"].nunique() < 2
        ):
            print(
                f"[Bootstrap mediation] {course_name} {profile_label}: "
                "insufficient variation; skip."
            )
            continue

        y = model_data["hw2_score"].to_numpy(dtype=float)
        x = model_data[x_col].to_numpy(dtype=float)
        mediator = model_data["proactive_critical"].to_numpy(dtype=float)
        control_matrix = (
            model_data[controls].to_numpy(dtype=float)
            if controls
            else np.empty((n, 0), dtype=float)
        )

        def _estimate(indices: np.ndarray) -> Optional[float]:
            sample_x = x[indices]
            sample_m = mediator[indices]
            if np.unique(sample_x).size < 2 or np.unique(sample_m).size < 2:
                return None
            sample_y = y[indices]
            sample_controls = control_matrix[indices]
            mediator_design = np.column_stack(
                [np.ones(len(indices)), sample_x, sample_controls]
            )
            adjusted_design = np.column_stack(
                [np.ones(len(indices)), sample_x, sample_m, sample_controls]
            )
            try:
                mediator_coef = np.linalg.lstsq(
                    mediator_design, sample_m, rcond=None
                )[0]
                adjusted_coef = np.linalg.lstsq(
                    adjusted_design, sample_y, rcond=None
                )[0]
            except np.linalg.LinAlgError:
                return None

            a = float(mediator_coef[1])
            b = float(adjusted_coef[2])
            return a * b

        point = _estimate(np.arange(n))
        if point is None:
            print(
                f"[Bootstrap mediation] {course_name} {profile_label}: "
                "point estimate failed; skip."
            )
            continue

        bootstrap_estimates: List[float] = []
        attempts = 0
        max_attempts = max(n_boot * 5, n_boot + 100)
        while len(bootstrap_estimates) < n_boot and attempts < max_attempts:
            attempts += 1
            estimate = _estimate(rng.integers(0, n, size=n))
            if estimate is None:
                continue
            bootstrap_estimates.append(estimate)

        successful_boot = len(bootstrap_estimates)
        if successful_boot < n_boot:
            print(
                f"[Bootstrap mediation] {course_name} {profile_label}: "
                f"only {successful_boot}/{n_boot} valid resamples."
            )

        values = np.asarray(bootstrap_estimates, dtype=float)
        ci_low, ci_high = (
            np.percentile(values, [2.5, 97.5])
            if len(values)
            else (float("nan"), float("nan"))
        )
        rows.append(
            {
                "course": course_name,
                "profile": profile_label,
                "indirect_ab": point,
                "boot_se": float(np.std(values, ddof=1))
                if len(values) > 1
                else float("nan"),
                "ci_low": float(ci_low),
                "ci_high": float(ci_high),
                "n": n,
                "n_boot": successful_boot,
                "ci_excludes_zero": bool(ci_low > 0 or ci_high < 0),
            }
        )

    return pd.DataFrame(rows) if rows else None


def report_bootstrap_indirect_association(
    metrics: Optional[pd.DataFrame],
    course_name: str,
) -> None:
    """Print the bootstrap indirect association for each learner profile."""
    if metrics is None or metrics.empty:
        return

    print(f"\n[Bootstrap indirect association] {course_name} (Experiment only)")
    print("  X encoding: Low=1, Mid=2, High=3; M: proactive_critical=1, passive=0")
    for _, row in metrics.iterrows():
        marker = " *" if bool(row["ci_excludes_zero"]) else ""
        print(
            f"  {row['profile']} (n={int(row['n'])}, "
            f"bootstrap={int(row['n_boot'])}): "
            f"a*b={row['indirect_ab']:+.4f} "
            f"[95% CI {row['ci_low']:+.4f}, {row['ci_high']:+.4f}]{marker}"
        )


def report_behavior_prediction_from_university_and_prior(df: pd.DataFrame, course_name: str) -> None:
    df_exp = df[df["group"] == 1].copy()
    if df_exp.empty:
        print(f"[Behavior prediction] No Experiment users for {course_name}; skip.")
        return

    if "university_cat" not in df_exp.columns:
        df_exp["university_cat"] = df_exp["university_ranking_num"].apply(normalize_university_ranking_from_num)
    if "capability_cat" not in df_exp.columns:
        df_exp["capability_cat"] = df_exp["captest_score"].apply(
            lambda x: categorize_capability_from_score(x, course_name.lower())
        )

    required_cols = ["behavior_supergroup", "university_cat", "capability_cat"]
    sub = df_exp[required_cols].dropna().copy()
    if sub.empty or len(sub) < 5:
        print(f"[Behavior prediction] Not enough data for {course_name}; skip.")
        return

    def _order_levels(values: pd.Series) -> List[str]:
        raw = [str(v) for v in values.unique().tolist()]
        preferred = ["Low", "Mid", "High"]
        ordered = [v for v in preferred if v in raw]
        for v in raw:
            if v not in ordered:
                ordered.append(v)
        return ordered

    uni_levels = _order_levels(sub["university_cat"])
    cap_levels = _order_levels(sub["capability_cat"])
    if not uni_levels or not cap_levels:
        print(f"[Behavior prediction] Missing categories for {course_name}; skip.")
        return

    sub["university_cat"] = pd.Categorical(sub["university_cat"].astype(str), categories=uni_levels, ordered=True)
    sub["capability_cat"] = pd.Categorical(sub["capability_cat"].astype(str), categories=cap_levels, ordered=True)
    sub["behavior_supergroup"] = sub["behavior_supergroup"].astype(str)

    # Linear numeric encoding for university/capability: Low->1, Mid->2, High->3 (based on ordered levels)
    uni_map = {level: idx + 1 for idx, level in enumerate(uni_levels)}
    cap_map = {level: idx + 1 for idx, level in enumerate(cap_levels)}
    sub["university_cat_num"] = sub["university_cat"].map(uni_map).astype(float)
    sub["capability_cat_num"] = sub["capability_cat"].map(cap_map).astype(float)

    # Binary behavior outcome: proactive_critical vs passive
    sub["proactive_critical"] = (sub["behavior_supergroup"] == "proactive_critical").astype(float)

    def _fit_and_report(formula: str, term: str, label: str) -> None:
        try:
            model = smf.ols(formula, data=sub).fit()
        except Exception as exc:
            print(f"[Behavior prediction] {course_name} {label} model failed: {exc}")
            return
        terms = _extract_term_stats(model, term)
        if not terms:
            print(f"[Behavior prediction] {course_name} {label}: N/A")
            return
        coef, pval = list(terms.values())[0]
        sig = " *" if pval < 0.05 else ""
        print(
            f"  {label}: coef={coef:+.4f} (p={pval:.3g}){sig}"
        )

    print(f"\n[Behavior prediction] {course_name} (Experiment only)")
    print(f"  Numeric encoding: university_cat={uni_map}, capability_cat={cap_map}")
    _fit_and_report("proactive_critical ~ university_cat_num", "university_cat_num", "University -> Behavior")
    _fit_and_report("proactive_critical ~ capability_cat_num", "capability_cat_num", "Prior -> Behavior")

    # Merge Mid/High vs Low for university
    # Direct proportion difference test: Mid/High vs Low
    is_low = sub["university_cat"].astype(str) == "Low"
    n_low = int(is_low.sum())
    n_mh = int((~is_low).sum())
    if n_low == 0 or n_mh == 0:
        print("  University (Mid/High vs Low): N/A")
        return
    succ_low = float(sub.loc[is_low, "proactive_critical"].sum())
    succ_mh = float(sub.loc[~is_low, "proactive_critical"].sum())
    try:
        # One-sided test: Mid/High proportion > Low proportion
        stat, pval = proportions_ztest([succ_mh, succ_low], [n_mh, n_low], alternative="larger")
    except Exception as exc:
        print(f"[Behavior prediction] {course_name} University (Mid/High vs Low) test failed: {exc}")
        return
    p_low = succ_low / n_low if n_low else float("nan")
    p_mh = succ_mh / n_mh if n_mh else float("nan")
    diff = p_mh - p_low
    sig = " *" if pval < 0.05 else ""
    print(
        f"  University (Mid/High vs Low): Δp={diff:+.4f} "
        f"(p={pval:.3g}){sig} [p_low={p_low:.3f}, p_mid_high={p_mh:.3f}]"
    )

_INEQUALITY_RUN_SOURCE = '# Run Block 1\nprint("=" * 80)\nprint("Generating Unweighted Equity Analysis")\nprint("=" * 80)\n\nprint("\\nStep 1: Loading base data...")\npython_df, math_df = load_valid_users(VALIDUSER_FILE)\npresurvey = load_presurvey_data(PRESURVEY_FILE)\n\nprint("\\nStep 2: Merging presurvey data...")\npython_df = merge_presurvey_to_df(python_df, presurvey, "python")\nmath_df = merge_presurvey_to_df(math_df, presurvey, "math")\n\nprint("\\nStep 3: Loading capability scores...")\npy_captest, math_captest = load_capability_scores(REPO_ROOT / "data/annotation/captest_scores.json")\npython_df = python_df.merge(py_captest, on="username", how="left")\nmath_df = math_df.merge(math_captest, on="username", how="left")\n\nprint("\\nStep 4: Loading homework scores...")\npy_homework, math_homework = load_homework_scores(\n    py_scores_file=PYTHON_SCORE_FILE,\n    math_scores_file=MATH_SCORE_FILE,\n    math_hw1_problems=MATH_HW1_PROBLEMS,\n    math_hw2_problems=MATH_HW2_PROBLEMS,\n    math_score_map=MATH_SCORE_MAP,\n)\npython_df = python_df.merge(py_homework, on="username", how="left")\nmath_df = math_df.merge(math_homework, on="username", how="left")\n\nprint("\\nStep 5: Preparing covariates...")\npython_df = prepare_covariates(python_df, "python")\nmath_df = prepare_covariates(math_df, "math")\n\nprint("\\nStep 6: Adding capability categories...")\npython_df["captest_tertile"] = python_df["captest_score"].apply(\n    lambda x: categorize_capability_from_score(x, "python")\n)\nmath_df["captest_tertile"] = math_df["captest_score"].apply(\n    lambda x: categorize_capability_from_score(x, "math")\n)\n\nprint("\\nStep 6a: Interaction tests (unweighted)...")\npython_df["university_cat"] = python_df["university_ranking_num"].apply(\n    normalize_university_ranking_from_num\n)\npython_df["capability_cat"] = python_df["captest_score"].apply(\n    lambda x: categorize_capability_from_score(x, "python")\n)\nmath_df["university_cat"] = math_df["university_ranking_num"].apply(\n    normalize_university_ranking_from_num\n)\nmath_df["capability_cat"] = math_df["captest_score"].apply(\n    lambda x: categorize_capability_from_score(x, "math")\n)\n_run_binned_numeric_model(python_df, "university_cat", "Python University rank")\n_run_binned_numeric_model(python_df, "capability_cat", "Python Prior knowledge")\n_run_binned_numeric_model(math_df, "university_cat", "Math University rank")\n_run_binned_numeric_model(math_df, "capability_cat", "Math Prior knowledge")\n\nprint("\\nStep 7: Generating plots (unweighted, per-course)...")\noutput_file = FIGURES_DIR / "inequal_unweighted.pdf"\nplot_equity(python_df, math_df, output_file, show=SHOW_FIGURES)\n\nprint("\\nStep 7a: Adding behavior supergroups (Experiment only)...")\npython_df = add_behavior_supergroup_python(python_df)\nmath_df = add_behavior_supergroup_math(math_df)\n\nprint("\\nStep 7b: Explained variance + behavior vs Experiment equity plots...")\nprint("=" * 80)\nprint("Coefficient Shift Analysis (Behavior Contribution)")\nprint("=" * 80)\npython_ev_metrics = compute_explained_variance_behavior_metrics(python_df, "Python")\nmath_ev_metrics = compute_explained_variance_behavior_metrics(math_df, "Math")\nreport_explained_variance_behavior(python_df, "Python", metrics=python_ev_metrics)\nreport_explained_variance_behavior(math_df, "Math", metrics=math_ev_metrics)\n\nPROACTIVE_CRITICAL_COLOR = "#31a354"\nPASSIVE_COLOR = "#7f7f7f"\n_plot_behavior_vs_exp_lines_combined(\n    df=python_df,\n    course_name="Python",\n    proactive_critical_color=PROACTIVE_CRITICAL_COLOR,\n    passive_color=PASSIVE_COLOR,\n    output_path=FIGURES_DIR / "inequal_behavior_combined_python.pdf",\n    show=SHOW_FIGURES,\n    explained_metrics=python_ev_metrics,\n)\n_plot_behavior_vs_exp_lines_combined(\n    df=math_df,\n    course_name="Math",\n    proactive_critical_color=PROACTIVE_CRITICAL_COLOR,\n    passive_color=PASSIVE_COLOR,\n    output_path=FIGURES_DIR / "inequal_behavior_combined_math.pdf",\n    show=SHOW_FIGURES,\n    explained_metrics=math_ev_metrics,\n)\n\nprint("\\nStep 8: Generating A1 behavior-group proportion plots (Python, Experiment)...")\nbehavior_out = FIGURES_DIR / "a1_behavior_group_proportions_python_exp.pdf"\nplot_python_a1_behavior_group_proportions(python_df, behavior_out, show=SHOW_FIGURES)\nprint("\\nStep 8a: Predicting A1 behavior from university/prior (Python, Experiment)...")\nreport_behavior_prediction_from_university_and_prior(python_df, "Python")\n\nprint("\\nStep 9: Generating A1 behavior-group proportion plots (Math, Experiment)...")\nmath_behavior_out = FIGURES_DIR / "a1_behavior_group_proportions_math_exp.pdf"\nplot_math_a1_behavior_group_proportions(math_df, math_behavior_out, show=SHOW_FIGURES)\nprint("\\nStep 9a: Predicting A1 behavior from university/prior (Math, Experiment)...")\nreport_behavior_prediction_from_university_and_prior(math_df, "Math")\n\nprint("\\n" + "=" * 80)\nprint("Unweighted Equity Analysis Complete")\nprint("=" * 80)\n'

def run_background_behavior_inequality_analysis(*, figures_dir: Optional[Path] = None, show_figures: bool = False) -> dict[str, Any]:
    """Generate the figures and statistics for AI-use variation by background."""
    global FIGURES_DIR, SHOW_FIGURES, output_file
    FIGURES_DIR = Path(figures_dir) if figures_dir is not None else REPO_ROOT / "figures"
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    SHOW_FIGURES = bool(show_figures)
    exec(_INEQUALITY_RUN_SOURCE, globals(), globals())
    return {
        "output_files": [
            FIGURES_DIR / "a1_behavior_group_proportions_python_exp.pdf",
            FIGURES_DIR / "a1_behavior_group_proportions_math_exp.pdf",
            FIGURES_DIR / "inequal_behavior_combined_python.pdf",
            FIGURES_DIR / "inequal_behavior_combined_math.pdf",
            FIGURES_DIR / "inequal_unweighted_python.pdf",
            FIGURES_DIR / "inequal_unweighted_game_theory.pdf",
        ]
    }
