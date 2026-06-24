"""Helper functions behind the reviewer-facing behavior heterogeneity notebook.

The notebook is intentionally short. This module keeps the original parsing,
classification, statistical testing, and publication-style plotting code in one
importable place so automated tests and notebooks share the same implementation.
"""
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
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import statsmodels.formula.api as smf
from statsmodels.stats.proportion import proportions_ztest

from analyze.utils.display import relative_path
from analyze.behavior.category_rules import (
    MATH_A1_PRECEDENCE,
    PYTHON_A1_PRECEDENCE,
    pick_math_a1_category,
    pick_python_a1_category,
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

# Canonical behavior labels used in reviewer-facing notebooks and figures.
PY_BEHAVIOR_LABELS = {
    "no_chat": "Abstention",
    "mindless_copy": "Rote-adoption",
    "try_then_ask": "Active-trial",
    "ask_then_explain": "Verification",
}
PY_BEHAVIOR_ORDER = list(dict.fromkeys(PY_BEHAVIOR_LABELS.values()))

MATH_BEHAVIOR_LABELS = {
    "no_chat": "Abstention",
    "mindless_copy": "Rote-adoption",
    "try_then_ask": "Active-trial",
    "fix_after_wrong": "Error-correction",
    "challenge_wrong": "Verification",
    "ask_then_explain": "Verification",
}
MATH_BEHAVIOR_ORDER = list(dict.fromkeys(MATH_BEHAVIOR_LABELS.values()))

BEHAVIOR_FIGURE_COLORS = {
    "Abstention": "#c6dbef",
    "Rote-adoption": "#9ecae1",
    "Active-trial": "#a1d99b",
    "Verification": "#238b45",
    "Error-correction": "#74c476",
}


def use_canonical_behavior_labels(feats: List[Any], *, course: str) -> List[Any]:
    """Replace internal classifier category codes with canonical behavior labels."""
    if course == "python":
        labels = PY_BEHAVIOR_LABELS
    elif course == "math":
        labels = MATH_BEHAVIOR_LABELS
    else:
        raise ValueError(f"Unknown course for behavior labels: {course!r}")

    for feature in feats:
        feature.category = labels.get(feature.category, feature.category)
    return feats




# Shared constants and parsing helpers used by the behavior notebooks.
LABEL_TRIED_Y = "y"
LABEL_TRIED_N = "n"
VERBATIM_MODES = {"copy", "type"}
COPYLIKE_MODES = {"copy", "type", "mix"}
EXPLAIN_GOALS = {"explain"}
EXPLAIN_TYPES = {"concept"}
FINAL_ANSWER_GOALS = {"final_answer"}
FINAL_ANSWER_TYPES = {"answer"}

# Python behavior-classification defaults, matching the original combined script.
TRIED_THRESHOLD = 0.25
COPY_FIRST_THRESHOLD = 0.75
PRECEDENCE = PYTHON_A1_PRECEDENCE

def _set_nature_style_like_a1_behavior_analyze() -> None:
    """Use the same publication plotting style as the original behavior-analysis scripts."""
    matplotlib.rcParams.update({
        "figure.dpi": 300, "savefig.dpi": 300,
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 12, "axes.labelsize": 14, "axes.titlesize": 14,
        "xtick.labelsize": 12, "ytick.labelsize": 12, "axes.linewidth": 1.2,
        "xtick.major.width": 1.2, "ytick.major.width": 1.2,
        "xtick.major.size": 5.0, "ytick.major.size": 5.0,
        "xtick.direction": "out", "ytick.direction": "out",
        "axes.spines.top": False, "axes.spines.right": False,
        "figure.facecolor": "white", "axes.facecolor": "white",
        "axes.unicode_minus": False, "pdf.fonttype": 42, "ps.fonttype": 42,
    })

def _set_nature_style_v2() -> None:
    _set_nature_style_like_a1_behavior_analyze()

def _safe_get(d: dict, path: tuple[str, ...], default: object = None) -> object:
    """Read nested JSON fields without failing when an annotation field is missing."""
    cur: object = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

def _parse_correct_flag(value: object) -> bool | None:
    """Normalize correctness labels from booleans, 0/1 values, and y/n strings."""
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
    """Return whether any blank-level answer has the requested correctness value."""
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
    """Split blank-level answers into correct and incorrect blank id sets."""
    ok: set[str] = set()
    bad: set[str] = set()
    if not isinstance(blanks, dict):
        return ok, bad
    for k, v in blanks.items():
        if not isinstance(v, dict):
            continue
        flag = _parse_correct_flag(v.get("correct"))
        if flag is True:
            ok.add(str(k))
        elif flag is False:
            bad.add(str(k))
    return ok, bad



def _infer_target_problems_from_labels(labels_by_user: dict, *, stage: str, problem_prefix: str) -> list[str]:
    """Infer Assignment problem ids from chat-label records."""
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
            if isinstance(problem, str) and problem.startswith(problem_prefix):
                probs.add(problem)
    return sorted(probs)

def _blank_attempted(value: object) -> bool:
    """Treat non-empty non-placeholder blank values as attempted."""
    if value is None:
        return False
    s = str(value).strip()
    if not s:
        return False
    return "|" not in s

#%%
# =========================
# Block 2: Python A1 behavior analysis
# =========================
LABELS_PATH = _data_path("data/annotation/a1_chat_labels.json")
SCORES_PATH = REPO_ROOT / "data/annotation/python_scores.json"
DETAILS_PATH = REPO_ROOT / "data/annotation/python_details.json"
EXCLUDE_USERS_PATH = REPO_ROOT / "data/processed/exclude_user.csv"

GROUP = "Experiment"
STAGE = "a1"
PROBLEM_PREFIX = "py_"

DROP_UNK_ASK = True
APPLY_EXCLUDE_USERS = True

PROBLEM_DENOM_POLICY = "attempted_or_chatted"
NOCHAT_TRIED_IF_ATTEMPTED = True

TARGET_PROBLEMS: Optional[List[str]] = None

OUT_CSV: Optional[Path] = None

RUN_STATS = True
STATS_CATEGORIES: Tuple[str, ...] = ("no_chat", "mindless_copy", "try_then_ask", "ask_then_explain")

PLOT_CONTROL_VS_EXP = True
FIG_OUT_PDF: Optional[Path] = REPO_ROOT / "figures/a1_hw2_control_vs_exp_behavior.pdf"
PLOT_SHOW_N_IN_XTICK = True

RUN_PY_PLAGIARISM_EXTRA = True
SAVE_SINGLE_BEHAVIOR_HETEROGENEITY = False

RUN_PY_LLM_ACCURACY = True
PY_LLM_ACC_GROUP = "All"
FIG_PY_LLM_ACC_PDF: Optional[Path] = REPO_ROOT / "figures/a1_py_llm_accuracy_by_difficulty.pdf"


@dataclass(frozen=True)
class ChatLabel:
    timestamp: float
    problem: str
    pre_tried: str
    ask_type: str
    ask_goal: str
    post_mode: str
    ask_correct: Optional[bool] = None


@dataclass
class UserFeatures:
    user_id: str
    n_chats: int
    n_problems: int
    tried_rate: float
    mindless_copy_rate: float
    any_answer_copy_rate: float
    ask_then_explain: bool
    verbatim_rate: float
    adapt_rate: float
    none_rate: float
    category: str
    hw2: Optional[float]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def safe_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        if isinstance(x, bool):
            return float(x)
        v = float(x)
        if math.isnan(v):
            return None
        return v
    except Exception:
        return None


def wilson_ci(k: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    if n <= 0:
        return 0.0, 0.0
    p = k / float(n)
    denom = 1.0 + (z * z) / n
    center = (p + (z * z) / (2 * n)) / denom
    half = (z / denom) * math.sqrt((p * (1 - p) + (z * z) / (4 * n)) / n)
    return max(0.0, center - half), min(1.0, center + half)


def load_exclude_users(path: Path) -> set[str]:
    if not path.exists():
        return set()
    out: set[str] = set()
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if not isinstance(row, dict):
                continue
            u = (row.get("username") or "").strip()
            if u:
                out.add(u)
    return out


def infer_target_problems_from_labels(labels_by_user: Dict[str, Any], *, stage: str, problem_prefix: str) -> List[str]:
    return _infer_target_problems_from_labels(labels_by_user, stage=stage, problem_prefix=problem_prefix)


def build_user_problem_attempted_map(
    user_problem_chats: Dict[str, Dict[str, List[ChatLabel]]],
    details: Dict[str, Any],
) -> Dict[str, Dict[str, bool]]:
    out: Dict[str, Dict[str, bool]] = {}
    for uid, pmap in user_problem_chats.items():
        drec = details.get(uid, {}) if isinstance(details.get(uid, {}), dict) else {}
        dprobs = drec.get("problems", {}) if isinstance(drec.get("problems", {}), dict) else {}
        amap: Dict[str, bool] = {}
        for p in pmap.keys():
            prec = dprobs.get(p, {})
            attempted = isinstance(prec, dict) and (prec.get("user_answer") is not None)
            amap[p] = bool(attempted)
        out[uid] = amap
    return out


def iter_labeled_py_chats(
    labels_by_user: Dict[str, Any],
    user_id: str,
    *,
    stage: str,
    problem_prefix: str,
    drop_unk_ask: bool,
) -> List[ChatLabel]:
    user_blob = labels_by_user.get(user_id, {})
    if not isinstance(user_blob, dict) or not user_blob:
        return []

    out: List[ChatLabel] = []
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

        label = rec.get("label") or {}
        pre_tried = str(_safe_get(label, ("pre", "tried"), default="unk"))
        ask_type = str(_safe_get(label, ("ask", "type"), default="unk"))
        ask_goal = str(_safe_get(label, ("ask", "goal"), default="unk"))
        ask_correct = _parse_correct_flag(_safe_get(label, ("ask", "correct"), default=None))
        post_mode = str(_safe_get(label, ("post", "mode"), default="unk"))

        if drop_unk_ask and ask_type == "unk":
            continue

        ts = rec.get("timestamp")
        try:
            ts_f = float(ts)
        except Exception:
            ts_f = float("nan")

        out.append(
            ChatLabel(
                timestamp=ts_f,
                problem=problem,
                pre_tried=pre_tried,
                ask_type=ask_type,
                ask_goal=ask_goal,
                post_mode=post_mode,
                ask_correct=ask_correct,
            )
        )

    out.sort(key=lambda x: (x.problem, x.timestamp))
    return out


def compute_single_problem_features(
    chats_in_problem: List[ChatLabel],
    *,
    attempted_without_chat: bool,
    nochat_tried_if_attempted: bool,
) -> Dict[str, Any]:
    if not chats_in_problem:
        return {
            "n_chats": 0,
            "tried_any": bool(attempted_without_chat and nochat_tried_if_attempted),
            "mindless_copy": False,
            "any_answer_copy": False,
            "ask_then_explain": False,
        }

    seq = sorted(chats_in_problem, key=lambda c: c.timestamp)
    tried_any = any(c.pre_tried == LABEL_TRIED_Y for c in seq)

    mindless_copy = any(
        (((c.ask_type in FINAL_ANSWER_TYPES) or (c.ask_goal in FINAL_ANSWER_GOALS)) and (c.pre_tried == LABEL_TRIED_N))
        for c in seq
    )

    any_answer_copy = any(
        ((c.ask_type in FINAL_ANSWER_TYPES) or (c.ask_goal in FINAL_ANSWER_GOALS))
        and (c.post_mode in COPYLIKE_MODES)
        for c in seq
    )

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

    return {
        "n_chats": len(seq),
        "tried_any": bool(tried_any),
        "mindless_copy": bool(mindless_copy),
        "any_answer_copy": bool(any_answer_copy),
        "ask_then_explain": bool(ask_then_explain),
    }


def compute_problem_features_map(
    problem_chats: Dict[str, List[ChatLabel]],
    problem_attempted_without_chat: Dict[str, bool],
    *,
    nochat_tried_if_attempted: bool,
) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for p, seq in problem_chats.items():
        out[p] = compute_single_problem_features(
            seq,
            attempted_without_chat=bool(problem_attempted_without_chat.get(p, False)),
            nochat_tried_if_attempted=nochat_tried_if_attempted,
        )
    return out


def pick_category(
    n_chats: int,
    tried_rate_problem: float,
    mindless_copy_rate_problem: float,
    ask_then_explain: bool,
    *,
    tried_threshold: float,
    copy_first_threshold: float,
    precedence: Tuple[str, ...],
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


def build_user_problem_chats(
    labels: Dict[str, Any],
    scores: Dict[str, Any],
    details: Dict[str, Any],
    *,
    group: str,
    stage: str,
    problem_prefix: str,
    drop_unk_ask: bool,
    target_problems: List[str],
    problem_denom_policy: str,
    excluded_users: set[str],
) -> Dict[str, Dict[str, List[ChatLabel]]]:
    users = [
        uid
        for uid, s in scores.items()
        if isinstance(s, dict) and s.get("group") == group and uid not in excluded_users
    ]
    users.sort()

    out: Dict[str, Dict[str, List[ChatLabel]]] = {}
    for uid in users:
        chats = iter_labeled_py_chats(
            labels,
            uid,
            stage=stage,
            problem_prefix=problem_prefix,
            drop_unk_ask=drop_unk_ask,
        )
        by_prob: Dict[str, List[ChatLabel]] = defaultdict(list)
        for c in chats:
            by_prob[c.problem].append(c)

        drec = details.get(uid, {}) if isinstance(details.get(uid, {}), dict) else {}
        dprobs = drec.get("problems", {}) if isinstance(drec.get("problems", {}), dict) else {}

        def _attempted(problem_id: str) -> bool:
            prec = dprobs.get(problem_id, {})
            if not isinstance(prec, dict):
                return False
            return prec.get("user_answer") is not None

        included: Dict[str, List[ChatLabel]] = {}
        for p in target_problems:
            has_chat = p in by_prob and len(by_prob[p]) > 0
            attempted = _attempted(p)

            if problem_denom_policy == "chatted_only":
                if not has_chat:
                    continue
            elif problem_denom_policy == "attempted_or_chatted":
                if not (has_chat or attempted):
                    continue
            elif problem_denom_policy == "all_in_problem_set":
                pass
            else:
                raise ValueError(f"Unknown PROBLEM_DENOM_POLICY={problem_denom_policy!r}")

            included[p] = sorted(by_prob.get(p, []), key=lambda x: x.timestamp)

        out[uid] = included
    return out


def compute_single_user_features(
    user_id: str,
    problem_chats: Dict[str, List[ChatLabel]],
    problem_attempted_without_chat: Dict[str, bool],
    score_rec: Dict[str, Any],
    *,
    tried_threshold: float,
    copy_first_threshold: float,
    precedence: Tuple[str, ...],
    nochat_tried_if_attempted: bool,
) -> UserFeatures:
    hw2 = safe_float(score_rec.get("HW2"))

    n_problems = len(problem_chats)
    n_chats = sum(len(v) for v in problem_chats.values())

    if n_problems == 0:
        tried_rate = 0.0
        mindless_copy_rate = 0.0
        any_answer_copy_rate = 0.0
        ask_then_explain = False
        verbatim_rate = 0.0
        adapt_rate = 0.0
        none_rate = 0.0
    else:
        prob_feats = compute_problem_features_map(
            problem_chats,
            problem_attempted_without_chat,
            nochat_tried_if_attempted=nochat_tried_if_attempted,
        )

        tried_rate = sum(1 for f in prob_feats.values() if f["tried_any"]) / len(prob_feats) if prob_feats else 0.0
        mindless_copy_rate = sum(1 for f in prob_feats.values() if f["mindless_copy"]) / len(prob_feats) if prob_feats else 0.0
        any_answer_copy_rate = sum(1 for f in prob_feats.values() if f["any_answer_copy"]) / len(prob_feats) if prob_feats else 0.0
        ask_then_explain = any(f["ask_then_explain"] for f in prob_feats.values())

        all_chats = [c for seq in problem_chats.values() for c in seq]
        if not all_chats:
            verbatim_rate = 0.0
            adapt_rate = 0.0
            none_rate = 0.0
        else:
            verbatim_rate = sum(1 for c in all_chats if c.post_mode in VERBATIM_MODES) / len(all_chats)
            adapt_rate = sum(1 for c in all_chats if c.post_mode == "adapt") / len(all_chats)
            none_rate = sum(1 for c in all_chats if c.post_mode == "none") / len(all_chats)

    category = pick_category(
        n_chats,
        tried_rate,
        mindless_copy_rate,
        ask_then_explain,
        tried_threshold=tried_threshold,
        copy_first_threshold=copy_first_threshold,
        precedence=precedence,
    )

    return UserFeatures(
        user_id=user_id,
        n_chats=n_chats,
        n_problems=n_problems,
        tried_rate=tried_rate,
        mindless_copy_rate=mindless_copy_rate,
        any_answer_copy_rate=any_answer_copy_rate,
        ask_then_explain=ask_then_explain,
        verbatim_rate=verbatim_rate,
        adapt_rate=adapt_rate,
        none_rate=none_rate,
        category=category,
        hw2=hw2,
    )


def compute_all_user_features(
    user_problem_chats: Dict[str, Dict[str, List[ChatLabel]]],
    user_problem_attempted_without_chat: Dict[str, Dict[str, bool]],
    scores: Dict[str, Any],
    *,
    tried_threshold: float,
    copy_first_threshold: float,
    precedence: Tuple[str, ...],
    nochat_tried_if_attempted: bool,
) -> Dict[str, UserFeatures]:
    out: Dict[str, UserFeatures] = {}
    for uid, pmap in user_problem_chats.items():
        score_rec = scores.get(uid, {}) if isinstance(scores.get(uid, {}), dict) else {}
        attempted_map = user_problem_attempted_without_chat.get(uid, {})
        out[uid] = compute_single_user_features(
            uid,
            pmap,
            attempted_map,
            score_rec,
            tried_threshold=tried_threshold,
            copy_first_threshold=copy_first_threshold,
            precedence=precedence,
            nochat_tried_if_attempted=nochat_tried_if_attempted,
        )
    return out


def user_features_to_rows(feats: List[UserFeatures]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for f in feats:
        rows.append(
            {
                "user_id": f.user_id,
                "category": f.category,
                "n_chats": f.n_chats,
                "n_problems": f.n_problems,
                "tried_rate(problem)": f.tried_rate,
                "mindless_copy_rate(problem)": f.mindless_copy_rate,
                "any_answer_copy_rate(problem)": f.any_answer_copy_rate,
                "ask_then_explain": int(bool(f.ask_then_explain)),
                "verbatim_rate(chat)": f.verbatim_rate,
                "adapt_rate(chat)": f.adapt_rate,
                "none_rate(chat)": f.none_rate,
                "HW2": f.hw2,
            }
        )
    return rows


def maybe_to_dataframe(rows: List[Dict[str, Any]]):
    try:
        import pandas as pd  # type: ignore
    except Exception:
        return rows
    return pd.DataFrame(rows)


def summarize(values: List[float]) -> Dict[str, Optional[float]]:
    v = [x for x in values if x is not None and not math.isnan(x)]
    if not v:
        return {"n": 0, "mean": None, "median": None, "std": None}
    if len(v) == 1:
        return {"n": 1, "mean": v[0], "median": v[0], "std": 0.0}
    return {"n": len(v), "mean": statistics.mean(v), "median": statistics.median(v), "std": statistics.pstdev(v)}


def _try_import_stats():
    try:
        import scipy.stats  # type: ignore
    except Exception as e:
        raise RuntimeError("Missing dependency: scipy") from e
    return scipy.stats


def run_nonparametric_tests(values_by_category: Dict[str, List[float]], *, categories: Tuple[str, ...], label: str) -> None:
    scipy_stats = _try_import_stats()

    cats = [c for c in categories if c in values_by_category]
    groups = []
    for c in cats:
        groups.append([x for x in values_by_category.get(c, []) if x is not None and not math.isnan(x)])

    print(f"\nNon-parametric tests for {label}:")
    print("  categories:", ", ".join([f"{c}(n={len(g)})" for c, g in zip(cats, groups)]))

    eligible = [(c, g) for c, g in zip(cats, groups) if len(g) >= 2]
    if len(eligible) < 2:
        print("  Not enough data for Kruskal-Wallis (need >=2 categories with n>=2).")
        return

    elig_cats = [c for c, _ in eligible]
    elig_groups = [g for _, g in eligible]

    kw = scipy_stats.kruskal(*elig_groups, nan_policy="omit")
    print(f"  Kruskal-Wallis: H={kw.statistic:.4f}, p={kw.pvalue:.6g} (k={len(eligible)})")

    pairs = []
    for i in range(len(elig_cats)):
        for j in range(i + 1, len(elig_cats)):
            c1, c2 = elig_cats[i], elig_cats[j]
            g1, g2 = elig_groups[i], elig_groups[j]
            res = scipy_stats.mannwhitneyu(g1, g2, alternative="two-sided", method="auto")
            pairs.append((c1, c2, len(g1), len(g2), float(res.statistic), float(res.pvalue)))

    print("  Pairwise Mann-Whitney U (raw p-values):")
    print("\t".join(["pair", "n1", "n2", "U", "p_raw"]))
    for (c1, c2, n1, n2, u, p) in pairs:
        print("\t".join([f"{c1} vs {c2}", str(n1), str(n2), f"{u:.2f}", f"{p:.6g}"]))


def _maybe_import_matplotlib():
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except Exception:
        return None
    return plt


def _apply_nature_axes(ax, *, xlabel: Optional[str] = None, ylabel: Optional[str] = None) -> None:
    try:
        import matplotlib as mpl  # type: ignore
    except Exception:
        mpl = None
    if xlabel is not None:
        ax.set_xlabel(xlabel, color="black")
    if ylabel is not None:
        ax.set_ylabel(ylabel, color="black")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if mpl is not None:
        tick_fs_x = mpl.rcParams.get("xtick.labelsize", 12)
        tick_fs_y = mpl.rcParams.get("ytick.labelsize", 12)
        font_family = mpl.rcParams.get("font.family", "sans-serif")
        for lab in ax.get_xticklabels():
            lab.set_fontsize(tick_fs_x)
            lab.set_fontfamily(font_family)
        for lab in ax.get_yticklabels():
            lab.set_fontsize(tick_fs_y)
            lab.set_fontfamily(font_family)


def _plot_behavior_heterogeneity_heatmap(
    *,
    user_problem_chats: Dict[str, Dict[str, List[Any]]],
    user_problem_attempted_without_chat: Dict[str, Dict[str, bool]],
    target_problems: List[str],
    problem_features_fn: Any,
    out_pdf: Path,
    course_label: str,
    show: bool,
) -> None:
    pltx = _maybe_import_matplotlib()
    if pltx is None:
        print("\nHeterogeneity heatmap skipped (missing dependency: matplotlib). Install with: `uv add matplotlib`")
        return
    try:
        import numpy as np  # type: ignore
    except Exception:
        print("\nHeterogeneity heatmap skipped (missing dependency: numpy). Install with: `uv add numpy`")
        return

    behaviors = ["Abstention", "Rote", "Trial", "Verify", "Correct"]
    behavior_colors = {
        "Abstention": "#bdbdbd",
        "Rote": "#9ecae1",
        "Trial": "#a1d99b",
        "Verify": "#31a354",
        "Correct": "#74c476",
    }
    mat, users_sorted = _build_behavior_mix_matrix(
        user_problem_chats=user_problem_chats,
        user_problem_attempted_without_chat=user_problem_attempted_without_chat,
        target_problems=target_problems,
        problem_features_fn=problem_features_fn,
    )
    if mat is None or users_sorted is None:
        print(f"\n[Heterogeneity] No users/problems for {course_label}; skip.")
        return

    fig_h = max(2.6, min(6.8, 0.09 * len(users_sorted) + 1.4))
    fig, ax = pltx.subplots(figsize=(5.4, fig_h), dpi=300)
    _draw_behavior_mix_panel(
        ax=ax,
        mat=mat,
        users_sorted=users_sorted,
        behaviors=behaviors,
        behavior_colors=behavior_colors,
        course_label=course_label,
        show_legend=True,
    )

    fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.96])
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf, dpi=300, bbox_inches="tight")
    print(f"[Heterogeneity] Saved: {relative_path(out_pdf)}")
    if show:
        pltx.show()
    else:
        pltx.close(fig)


def _build_behavior_mix_matrix(
    *,
    user_problem_chats: Dict[str, Dict[str, List[Any]]],
    user_problem_attempted_without_chat: Dict[str, Dict[str, bool]],
    target_problems: List[str],
    problem_features_fn: Any,
):
    try:
        import numpy as np  # type: ignore
    except Exception:
        return None, None
    users = sorted(user_problem_chats.keys())
    if (not users) or (not target_problems):
        return None, None
    mat = np.zeros((len(users), 5), dtype=float)
    for i, uid in enumerate(users):
        pmap = user_problem_chats.get(uid, {})
        amap = user_problem_attempted_without_chat.get(uid, {})
        counts = np.zeros(5, dtype=float)
        for p in target_problems:
            seq = pmap.get(p, [])
            attempted_without_chat = bool(amap.get(p, False)) and (len(seq) == 0)
            pf = problem_features_fn(seq, p, attempted_without_chat)
            is_abstention = int(pf.get("n_chats", 0) or 0) == 0
            is_correction = bool(pf.get("fix_after_wrong", False))
            is_verification = bool(pf.get("ask_then_explain", False)) or bool(pf.get("challenge_wrong", False))
            is_trial = bool(pf.get("tried_any", False))
            is_rote = bool(pf.get("mindless_copy", False))
            if is_abstention:
                counts[0] += 1
            elif is_correction:
                counts[4] += 1
            elif is_verification:
                counts[3] += 1
            elif is_trial:
                counts[2] += 1
            elif is_rote:
                counts[1] += 1
        mat[i, :] = counts / float(len(target_problems))
    dominant = np.argmax(mat, axis=1)
    dom_val = np.max(mat, axis=1)
    order = np.lexsort((-dom_val, dominant))
    return mat[order, :], [users[idx] for idx in order.tolist()]


def _draw_behavior_mix_panel(
    *,
    ax,
    mat,
    users_sorted: List[str],
    behaviors: List[str],
    behavior_colors: Dict[str, str],
    course_label: str,
    show_legend: bool,
    show_y_axis: bool = True,
    show_percent_tick_labels: bool = True,
    y_axis_label: str = "Participants",
) -> None:
    import numpy as np  # type: ignore
    y = np.arange(len(users_sorted))
    left = np.zeros(len(users_sorted), dtype=float)
    for j, b in enumerate(behaviors):
        vals = mat[:, j]
        ax.barh(
            y,
            vals,
            left=left,
            height=0.85,
            color=behavior_colors[b],
            edgecolor="white",
            linewidth=0.4,
            label=b,
        )
        left += vals
    ax.set_xlim(0.0, 1.0)
    ax.set_xlabel("", fontsize=13)
    if course_label:
        ax.set_title(course_label, fontsize=13, pad=7)
    if show_y_axis and len(users_sorted) <= 25:
        ax.set_yticks(y)
        ax.set_yticklabels(users_sorted, fontsize=10)
    elif show_y_axis:
        ax.set_yticks([])
        ax.set_ylabel(y_axis_label, fontsize=14, labelpad=10)
    else:
        ax.set_yticks([])
        ax.set_ylabel("")
    if show_y_axis:
        ax.set_ylabel(y_axis_label, fontsize=14, labelpad=10)
    ax.invert_yaxis()
    ax.set_xticks([0.0, 0.25, 0.5, 0.75, 1.0])
    if show_percent_tick_labels:
        ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"], fontsize=14)
    else:
        ax.set_xticklabels(["0", "25", "50", "75", "100"], fontsize=14)
    ax.tick_params(axis="x", labelsize=14)
    ax.tick_params(axis="y", length=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle=":", linewidth=0.5, alpha=0.28)
    if show_legend:
        ax.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1.16),
            ncol=4,
            frameon=False,
            fontsize=12,
            handlelength=1.2,
            columnspacing=0.9,
            handletextpad=0.4,
        )


def _plot_behavior_heterogeneity_two_panel(
    *,
    py_user_problem_chats: Dict[str, Dict[str, List[Any]]],
    py_user_problem_attempted_without_chat: Dict[str, Dict[str, bool]],
    py_target_problems: List[str],
    py_problem_features_fn: Any,
    math_user_problem_chats: Dict[str, Dict[str, List[Any]]],
    math_user_problem_attempted_without_chat: Dict[str, Dict[str, bool]],
    math_target_problems: List[str],
    math_problem_features_fn: Any,
    out_pdf: Path,
    show: bool,
) -> None:
    pltx = _maybe_import_matplotlib()
    if pltx is None:
        print("\nTwo-panel heterogeneity plot skipped (missing dependency: matplotlib).")
        return
    py_mat, py_users = _build_behavior_mix_matrix(
        user_problem_chats=py_user_problem_chats,
        user_problem_attempted_without_chat=py_user_problem_attempted_without_chat,
        target_problems=py_target_problems,
        problem_features_fn=py_problem_features_fn,
    )
    math_mat, math_users = _build_behavior_mix_matrix(
        user_problem_chats=math_user_problem_chats,
        user_problem_attempted_without_chat=math_user_problem_attempted_without_chat,
        target_problems=math_target_problems,
        problem_features_fn=math_problem_features_fn,
    )
    if py_mat is None or math_mat is None:
        print("\nTwo-panel heterogeneity plot skipped (missing data).")
        return
    behaviors = ["Abstention", "Rote-adoption", "Active-trial", "Error-correction", "Verification"]
    colors = {behavior: BEHAVIOR_FIGURE_COLORS[behavior] for behavior in behaviors}
    # Make each panel slender (narrow + taller) for paper layout readability.
    fig_h = max(4.6, min(7.2, 0.08 * max(len(py_users), len(math_users)) + 3.0))
    fig, axes = pltx.subplots(1, 2, figsize=(8.2, fig_h), dpi=300, constrained_layout=False)
    _draw_behavior_mix_panel(
        ax=axes[0],
        mat=math_mat,
        users_sorted=math_users,
        behaviors=behaviors,
        behavior_colors=colors,
        course_label="",
        show_legend=False,
        show_y_axis=True,
        show_percent_tick_labels=False,
        y_axis_label="Individual participants (one participant per row)",
    )
    _draw_behavior_mix_panel(
        ax=axes[1],
        mat=py_mat,
        users_sorted=py_users,
        behaviors=behaviors,
        behavior_colors=colors,
        course_label="",
        show_legend=False,
        show_y_axis=False,
        show_percent_tick_labels=False,
    )
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        bbox_to_anchor=(0.54, 0.095),
        ncol=5,
        frameon=False,
        fontsize=15,
        handlelength=1.25,
        columnspacing=0.9,
        handletextpad=0.5,
    )
    # Keep x-label close to panels (not too low), with reserved bottom area for legend.
    fig.supxlabel("Share of assignment problems by behavior category (%)", y=0.175, fontsize=14)
    fig.subplots_adjust(left=0.095, right=0.995, top=0.98, bottom=0.255, wspace=0.12)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_pdf, dpi=300, bbox_inches="tight")
    print(f"[Heterogeneity] Saved twin-panel: {relative_path(out_pdf)}")
    if show:
        pltx.show()
    else:
        pltx.close(fig)


def _percentile(values: List[float], p: float) -> Optional[float]:
    v = sorted([x for x in values if x is not None and not math.isnan(x)])
    if not v:
        return None
    if p <= 0:
        return v[0]
    if p >= 100:
        return v[-1]
    k = (len(v) - 1) * (p / 100.0)
    f = int(math.floor(k))
    c = int(math.ceil(k))
    if f == c:
        return v[f]
    return v[f] + (v[c] - v[f]) * (k - f)


def _print_dist(title: str, values: List[float]) -> None:
    v = [x for x in values if x is not None and not math.isnan(x)]
    print(f"\n{title}")
    if not v:
        print("  (empty)")
        return
    print("  n =", len(v))
    print("  mean =", f"{statistics.mean(v):.4f}")
    print("  median =", f"{statistics.median(v):.4f}")
    for p in (0, 10, 25, 50, 75, 90, 100):
        pv = _percentile(v, p)
        print(f"  p{p:02d} =", "NA" if pv is None else f"{pv:.4f}")


def _is_no_tried_answer_copy(c: Any) -> bool:
    is_answer = (c.ask_type in FINAL_ANSWER_TYPES) or (c.ask_goal in FINAL_ANSWER_GOALS)
    return bool(is_answer and (c.pre_tried == LABEL_TRIED_N))


def _load_hw1_entry_ts_from_behaviors_db(db_path: Path, *, stage_name: str) -> Dict[str, float]:
    """
    Return user -> earliest timestamp for entering HW1, inferred from `progress` events:
      value.stage == stage_name (e.g., "完成作业 1").
    """
    import sqlite3

    if not db_path.exists():
        print("\nBehavior DB not found:", db_path)
        return {}
    con = sqlite3.connect(str(db_path))
    cur = con.cursor()
    cur.execute("SELECT username, timestamp, value FROM user_actions WHERE action=?", ("progress",))
    out: Dict[str, float] = {}
    for username, ts, value in cur.fetchall():
        if not isinstance(username, str):
            continue
        try:
            ts_f = float(ts)
        except Exception:
            continue
        try:
            v = json.loads(value) if isinstance(value, str) else value
        except Exception:
            v = None
        if not isinstance(v, dict):
            continue
        st = v.get("stage")
        if st is None:
            continue
        st_s = str(st).strip()
        if st_s != stage_name:
            continue
        if username not in out or ts_f < out[username]:
            out[username] = ts_f
    con.close()
    return out


def run_plagiarism_extra_analyses(
    *,
    label: str,
    feats: List[Any],
    user_problem_chats: Dict[str, Dict[str, List[Any]]],
    details: Dict[str, Any],
    target_problems: List[str],
    group_name: str,
    problem_features_fn: Any,
    behaviors_db_path: Path,
    hw1_entry_stage_name: str,
    output_prefix: str,
    figures_dir: Path,
    show: bool,
    active_trial_threshold: float,
    include_problem_and_cdf_figures: bool = False,
) -> None:
    print(f"\n[Extra analyses] Start ({label})")

    analysis_feats = feats
    analysis_user_problem_chats = user_problem_chats
    if group_name != "Experiment":
        print("  Note: GROUP != 'Experiment' (GROUP =", group_name, "). Extra analyses use current GROUP data.")

    chat_users = [f for f in analysis_feats if f.n_chats > 0]
    chat_user_ids = [f.user_id for f in chat_users]
    print("\nExclude no-chat users:")
    print("  original users:", len(analysis_feats))
    print("  users with >=1 labeled chat:", len(chat_users))

    def _get_problem_map(drec: Any) -> Dict[str, Any]:
        if not isinstance(drec, dict):
            return {}
        probs = drec.get("problems")
        if isinstance(probs, dict):
            return probs
        return drec

    print("\nAll-Problems Pre-Tried (Among Participants With Chat):")
    problems_hw1 = list(target_problems) if target_problems else []
    if not problems_hw1:
        print("  target_problems missing; cannot compute.")
    else:
        all_pretried_ids: List[str] = []
        for uid in chat_user_ids:
            pmap = analysis_user_problem_chats.get(uid, {})
            drec = details.get(uid, {})
            dprobs = _get_problem_map(drec)

            def _attempted(problem_id: str) -> bool:
                prec = dprobs.get(problem_id, {})
                return isinstance(prec, dict) and (prec.get("user_answer") is not None)

            ok = True
            for p in problems_hw1:
                seq = pmap.get(p, [])
                pf = problem_features_fn(seq, p, _attempted(p))
                if not bool(pf.get("tried_any")):
                    ok = False
                    break
            if ok:
                all_pretried_ids.append(uid)

        n_total_chat = len(chat_user_ids)
        n_all_pretried = len(all_pretried_ids)
        print(f"  participants_with_chat: {n_total_chat}")
        print(
            f"  participants_all_{len(problems_hw1)}_pre_tried: "
            f"{n_all_pretried} ({(n_all_pretried / n_total_chat if n_total_chat else 0.0):.1%})"
        )
        if all_pretried_ids:
            print("  example_participants_all_pre_tried:", ", ".join(all_pretried_ids[:10]))

    user_plagiarism_ratio: List[float] = []
    user_trial_ratio: List[float] = []
    user_correction_verification_ratio: List[float] = []
    if not problems_hw1:
        print("  Warning: target_problems missing; Figure 1 will fall back to per-user included problems.")

    for uid in chat_user_ids:
        pmap = analysis_user_problem_chats.get(uid, {})
        drec = details.get(uid, {})
        dprobs = _get_problem_map(drec)

        def _attempted(problem_id: str) -> bool:
            prec = dprobs.get(problem_id, {})
            return isinstance(prec, dict) and (prec.get("user_answer") is not None)

        if problems_hw1:
            plag_count = 0
            trial_count = 0
            corr_ver_count = 0
            for p in problems_hw1:
                seq = pmap.get(p, [])
                if any(_is_no_tried_answer_copy(c) for c in seq):
                    plag_count += 1
                pf = problem_features_fn(seq, p, _attempted(p))
                if bool(pf.get("tried_any", False)):
                    trial_count += 1
                if bool(pf.get("ask_then_explain", False)) or bool(pf.get("challenge_wrong", False)) or bool(
                    pf.get("fix_after_wrong", False)
                ):
                    corr_ver_count += 1
            user_plagiarism_ratio.append(plag_count / float(len(problems_hw1)))
            user_trial_ratio.append(trial_count / float(len(problems_hw1)))
            user_correction_verification_ratio.append(corr_ver_count / float(len(problems_hw1)))
        else:
            denom = len(pmap)
            if denom <= 0:
                continue
            plag_count = sum(1 for _p, seq in pmap.items() if any(_is_no_tried_answer_copy(c) for c in seq))
            user_plagiarism_ratio.append(plag_count / float(denom))
            trial_count = 0
            corr_ver_count = 0
            for p, seq in pmap.items():
                pf = problem_features_fn(seq, p, _attempted(p))
                if bool(pf.get("tried_any", False)):
                    trial_count += 1
                if bool(pf.get("ask_then_explain", False)) or bool(pf.get("challenge_wrong", False)) or bool(
                    pf.get("fix_after_wrong", False)
                ):
                    corr_ver_count += 1
            user_trial_ratio.append(trial_count / float(denom))
            user_correction_verification_ratio.append(corr_ver_count / float(denom))

    _print_dist("Participant-Level Plagiarized Problem Ratio", user_plagiarism_ratio)
    _print_dist("Participant-Level Trial Problem Ratio", user_trial_ratio)
    _print_dist("Participant-Level Correction/Verification Problem Ratio", user_correction_verification_ratio)

    problem_plag_n = defaultdict(int)
    problem_denom_n = defaultdict(int)

    if problems_hw1:
        problems_all = [p for p in problems_hw1]
    else:
        problems_all = sorted({p for uid in chat_user_ids for p in analysis_user_problem_chats.get(uid, {}).keys()})

    for uid in chat_user_ids:
        pmap = analysis_user_problem_chats.get(uid, {})
        drec = details.get(uid, {})
        dprobs = _get_problem_map(drec)

        def _attempted(problem_id: str) -> bool:
            prec = dprobs.get(problem_id, {})
            return isinstance(prec, dict) and (prec.get("user_answer") is not None)

        for p in problems_all:
            seq = pmap.get(p, [])
            has_chat = bool(seq)
            attempted = _attempted(p)
            if has_chat or attempted:
                problem_denom_n[p] += 1
            if has_chat and any(_is_no_tried_answer_copy(c) for c in seq):
                problem_plag_n[p] += 1

    problem_plagiarism_ratio_by_problem: Dict[str, float] = {}
    for p in problems_all:
        denom = int(problem_denom_n.get(p, 0))
        if denom > 0:
            problem_plagiarism_ratio_by_problem[p] = problem_plag_n.get(p, 0) / float(denom)

    _print_dist(
        "Problem-Level Direct adoption rate (Denominator: Attempted Or Chatted)",
        list(problem_plagiarism_ratio_by_problem.values()),
    )

    first_copy_minutes: List[float] = []
    first_copy_minutes_within_20: List[float] = []
    users_with_copy_event: List[str] = []
    missing_start_ts = 0
    negative_durations = 0

    hw1_entry_ts = _load_hw1_entry_ts_from_behaviors_db(behaviors_db_path, stage_name=hw1_entry_stage_name)

    for uid in chat_user_ids:
        pmap = analysis_user_problem_chats.get(uid, {})
        all_chats = [c for seq in pmap.values() for c in seq if not math.isnan(c.timestamp)]
        if not all_chats:
            continue
        start_ts = hw1_entry_ts.get(uid)
        if start_ts is None:
            missing_start_ts += 1
            start_ts = min(c.timestamp for c in all_chats)
        copy_chats = [c for c in all_chats if _is_no_tried_answer_copy(c)]
        if not copy_chats:
            continue
        users_with_copy_event.append(uid)
        first_ts = min(c.timestamp for c in copy_chats)
        minutes = (first_ts - start_ts) / 60.0
        if minutes < 0:
            negative_durations += 1
        first_copy_minutes.append(minutes)
        if 0.0 <= minutes <= 20.0:
            first_copy_minutes_within_20.append(minutes)

    print("\nFirst Non-Pre-Tried Direct Adoption Time (Minutes Since HW1 Entry):")
    print("  users_with_event:", len(first_copy_minutes), "out of", len(chat_user_ids))
    print("  users_with_event_within_20m:", len(first_copy_minutes_within_20), "out of", len(chat_user_ids))
    print("  missing_HW1_entry_ts (fallback used):", missing_start_ts)
    print("  negative_durations (event before start):", negative_durations)
    no_event_ids = [uid for uid in chat_user_ids if uid not in set(users_with_copy_event)]
    print("  participants_with_no_detected_event:", len(no_event_ids))
    if no_event_ids:
        no_event_ids_sorted = sorted(no_event_ids)
        print("  participants_with_no_detected_event_ids:")
        print("   ", ", ".join(no_event_ids_sorted))
    _print_dist("First-copy time distribution (all minutes)", first_copy_minutes)
    _print_dist("First-copy time distribution (within 0–20 minutes)", first_copy_minutes_within_20)

    plt2 = _maybe_import_matplotlib()
    if plt2 is None:
        print("\nExtra figures skipped (missing dependency: matplotlib). Install with: `uv add matplotlib`")
        return

    _set_nature_style_v2()
    import numpy as np  # type: ignore

    EXTRA_FIGSIZE = (4.8, 3.2)
    EXTRA_BLUE = "#AECDE1"
    EXTRA_EDGE = "white"

    out_fig1 = figures_dir / f"{output_prefix}_user_plagiarism_ratio.pdf"
    out_fig1b = figures_dir / f"{output_prefix}_user_correction_verification_ratio.pdf"
    out_fig2 = figures_dir / f"{output_prefix}_problem_plagiarism_ratio.pdf"
    out_fig3 = figures_dir / f"{output_prefix}_first_no_tried_copy_time_cdf.pdf"

    fig1, ax1 = plt2.subplots(figsize=(3.6, 3.2))
    bins = np.linspace(0, 1, 11)
    vals = [x for x in user_trial_ratio if x is not None and not math.isnan(x)]
    if vals:
        weights = np.full(len(vals), 1.0 / len(vals), dtype=float)
        hist_vals, edges = np.histogram(vals, bins=bins, weights=weights)
        widths = np.diff(edges)
        lefts = edges[:-1]
        ax1.bar(
            lefts,
            hist_vals,
            width=widths,
            align="edge",
            color="#9ecae1",
            edgecolor=EXTRA_EDGE,
            linewidth=0.8,
        )
    else:
        ax1.bar([], [])
    ax1.set_xlim(0, 1)
    ax1.set_ylim(bottom=0)
    _apply_nature_axes(ax1, xlabel="Problem trial rate", ylabel="Participant proportion")
    fig1.tight_layout()
    out_fig1.parent.mkdir(parents=True, exist_ok=True)
    fig1.savefig(out_fig1, dpi=300, bbox_inches="tight")
    print("Saved:", relative_path(out_fig1))

    fig1b, ax1b = plt2.subplots(figsize=(3.6, 3.2))
    bins_b = np.linspace(0, 1, 11)
    vals_b = [x for x in user_correction_verification_ratio if x is not None and not math.isnan(x)]
    weights_b = [1.0 / len(vals_b) for _ in vals_b] if vals_b else None
    ax1b.hist(vals_b, bins=bins_b, weights=weights_b, color="#9ecae1", edgecolor=EXTRA_EDGE, linewidth=0.8)
    ax1b.set_xlim(0, 1)
    ax1b.set_ylim(bottom=0)
    _apply_nature_axes(
        ax1b,
        xlabel="Problem verify rate",
        ylabel="Participant proportion",
    )
    fig1b.tight_layout()
    out_fig1b.parent.mkdir(parents=True, exist_ok=True)
    fig1b.savefig(out_fig1b, dpi=300, bbox_inches="tight")
    print("Saved:", relative_path(out_fig1b))

    order = problems_all
    ys = [problem_plagiarism_ratio_by_problem[p] for p in order]
    xs = np.arange(len(order))
    xlabels = [p.split("/")[-1] if "/" in p else p for p in order]

    fig2 = None
    fig3 = None
    if include_problem_and_cdf_figures:
        fig2, ax2 = plt2.subplots(figsize=EXTRA_FIGSIZE)
        ax2.bar(xs, ys, color=EXTRA_BLUE, edgecolor=EXTRA_EDGE, linewidth=0.8)
        ax2.set_ylim(0, 1.0)
        ax2.set_xticks(xs)
        ax2.set_xticklabels(xlabels, rotation=0, ha="center")
        _apply_nature_axes(ax2, xlabel="Problem", ylabel="Direct adoption rate")
        fig2.tight_layout()
        out_fig2.parent.mkdir(parents=True, exist_ok=True)
        fig2.savefig(out_fig2, dpi=300, bbox_inches="tight")
        print("Saved:", relative_path(out_fig2))

        fig3, ax3 = plt2.subplots(figsize=EXTRA_FIGSIZE)
        time_vals = [x for x in first_copy_minutes if x is not None and not math.isnan(x)]
        time_clipped = [min(x, 20.0) for x in time_vals if x >= 0.0]
        time_within = [x for x in time_clipped if 0.0 <= x <= 20.0]
        ax3.axvline(20, color="#666666", linewidth=1.0, linestyle="--")
        ax3.set_xlim(0, 20)
        ax3.set_ylim(0, 1.0)
        _apply_nature_axes(ax3, xlabel="Time to first direct adoption (min)", ylabel="Cumulative proportion")
        n_total = len(chat_user_ids)
        xs_events = np.array(sorted(time_within), dtype=float) if time_within else np.array([], dtype=float)
        n_events_within = int(xs_events.size)
        if n_total > 0 and n_events_within > 0:
            ys_events = np.arange(1, n_events_within + 1, dtype=float) / float(n_total)
            xs_plot = np.concatenate(([0.0], xs_events, [20.0]))
            ys_plot = np.concatenate(([0.0], ys_events, [ys_events[-1]]))
            ax3.step(xs_plot, ys_plot, where="post", color=EXTRA_BLUE, linewidth=2.2)
            rug_h = 0.03
            ax3.vlines(xs_events, 0.0, rug_h, color=EXTRA_BLUE, linewidth=1.0, alpha=0.9)
            if n_events_within >= 4:
                q25, q50, q75 = np.percentile(xs_events, [25, 50, 75])
                for qx in (q25, q50, q75):
                    ax3.axvline(qx, ymin=0.0, ymax=0.12, color="#4D4D4D", linewidth=1.0, alpha=0.9)
        else:
            ax3.step([0.0, 20.0], [0.0, 0.0], where="post", color=EXTRA_BLUE, linewidth=2.2)
        fig3.tight_layout()
        out_fig3.parent.mkdir(parents=True, exist_ok=True)
        fig3.savefig(out_fig3, dpi=300, bbox_inches="tight")
        print("Saved:", relative_path(out_fig3))

    if show:
        plt2.show()
    else:
        for f in (fig1, fig1b, fig2, fig3):
            if f is None:
                continue
            plt2.close(f)


def _bh_adjust(pvals: List[float]) -> List[float]:
    if not pvals:
        return []
    m = len(pvals)
    order = sorted(range(m), key=lambda i: pvals[i])
    adjusted = [0.0] * m
    running_min = 1.0
    for rank, idx in enumerate(reversed(order), start=1):
        p = pvals[idx]
        adj = p * m / (m - rank + 1)
        running_min = min(running_min, adj)
        adjusted[idx] = min(running_min, 1.0)
    return adjusted


def print_control_vs_exp_tests(
    *,
    control_hw2: List[float],
    exp_hw2_by_behavior: Dict[str, List[float]],
    direction_by_group: Optional[Dict[str, str]] = None,
) -> None:
    try:
        scipy_stats = _try_import_stats()
    except Exception as e:
        print("\nControl-vs-Experiment tests skipped (missing dependency: scipy).")
        print("  Install with: `uv add scipy`")
        print("  Error:", repr(e))
        return

    def _clean(xs: List[float]) -> List[float]:
        out = []
        for x in xs:
            try:
                v = float(x)
            except Exception:
                continue
            if math.isnan(v):
                continue
            out.append(v)
        return out

    groups: Dict[str, List[float]] = {"Control": _clean(control_hw2)}
    for k, ys in exp_hw2_by_behavior.items():
        groups[k] = _clean(ys)

    print("\nControl vs Experiment (behavior groups) hypothesis tests (raw p-values):")
    for k, ys in groups.items():
        k1 = k.replace("\n", " ")
        if ys:
            print(f"  {k1}: n={len(ys)} mean={statistics.mean(ys):.3f} median={statistics.median(ys):.3f}")
        else:
            print(f"  {k1}: n=0")

    eligible = {k: ys for k, ys in groups.items() if len(ys) >= 2}
    if len(eligible) >= 2:
        kw = scipy_stats.kruskal(*eligible.values(), nan_policy="omit")
        print(f"\n  Kruskal–Wallis across groups: H={float(kw.statistic):.4f}, p={float(kw.pvalue):.6g} (k={len(eligible)})")
    else:
        print("\n  Kruskal–Wallis: not enough eligible groups (need >=2 groups with n>=2).")

    ctrl = groups.get("Control", [])
    if len(ctrl) < 2:
        print("\n  Pairwise Brunner–Munzel vs Control: not enough control samples (need n>=2).")
        return

    print("\n  Pairwise Brunner–Munzel vs Control (one-sided where specified):")
    print("\t".join(["group", "n_ctrl", "n_grp", "alt", "stat", "p_raw", "p_bh"]))
    group_rows = []
    for k, ys in groups.items():
        if k == "Control":
            continue
        if len(ys) < 2:
            continue
        k1 = k.replace("\n", " ")
        alt = (direction_by_group or {}).get(k)
        if alt not in {"greater", "less"}:
            print(f"  Brunner–Munzel direction missing for {k1}; skip pairwise tests.")
            return
        try:
            res = scipy_stats.brunnermunzel(ys, ctrl, alternative=alt)
        except TypeError:
            print("  Brunner–Munzel one-sided not supported by this scipy; skip pairwise tests.")
            return
        stat = float(res.statistic)
        p_bm = float(res.pvalue)
        group_rows.append((k1, len(ctrl), len(ys), alt, stat, p_bm))

    if not group_rows:
        return

    pvals = [r[5] for r in group_rows]
    p_bh = _bh_adjust(pvals)
    for (k1, n_ctrl, n_grp, alt, stat, p_raw), pb in zip(group_rows, p_bh):
        print(
            "\t".join(
                [
                    k1,
                    str(n_ctrl),
                    str(n_grp),
                    alt,
                    f"{stat:.4f}",
                    f"{p_raw:.6g}",
                    f"{pb:.6g}",
                ]
            )
        )


def plot_control_vs_exp_behaviors_hw2(
    *,
    control_hw2: List[float],
    exp_hw2_by_behavior: Dict[str, List[float]],
    exp_label_to_color: Optional[Dict[str, Any]] = None,
    out_pdf: Optional[Path] = None,
    show: bool = True,
    direction_by_group: Optional[Dict[str, str]] = None,
) -> None:
    plt = _maybe_import_matplotlib()
    if plt is None:
        print("\nPlot skipped (missing dependency: matplotlib). Install with: `uv add matplotlib`")
        return

    try:
        import numpy as np  # type: ignore
    except Exception:
        print("\nPlot skipped (missing dependency: numpy). Install with: `uv add numpy`")
        return

    _set_nature_style_v2()

    group_names = ["Control"] + list(exp_hw2_by_behavior.keys())
    data_list = [control_hw2] + [exp_hw2_by_behavior[k] for k in exp_hw2_by_behavior.keys()]

    filtered_data: List[List[float]] = []
    labels: List[str] = []
    for d, name in zip(data_list, group_names):
        clean_d = []
        for x in d:
            if x is None:
                continue
            try:
                v = float(x)
            except Exception:
                continue
            if math.isnan(v):
                continue
            clean_d.append(v)
        filtered_data.append(clean_d)
        labels.append(name)
    counts = [len(d) for d in filtered_data]
    means = [statistics.mean(d) if len(d) > 0 else float("nan") for d in filtered_data]
    adjusted_p_by_label: Dict[str, float] = {}

    control_color = "#C9C9C9"
    exp_blues = ["#c6dbef", "#9ecae1", "#6baed6", "#2171b5"]
    colors: List[Any] = [control_color]
    exp_names = labels[1:]
    for idx, name in enumerate(exp_names):
        if exp_label_to_color is not None and name in exp_label_to_color:
            colors.append(exp_label_to_color[name])
        else:
            if idx < len(exp_blues):
                colors.append(exp_blues[idx])
            else:
                colors.append(exp_blues[-1])
    if len(colors) < len(filtered_data):
        try:
            import matplotlib.cm as cm  # type: ignore

            cmap = cm.get_cmap("Blues")
            need = len(filtered_data) - len(colors)
            for t in [0.55 + 0.35 * (i / max(1, need - 1)) for i in range(need)]:
                colors.append(cmap(t))
        except Exception:
            colors = (colors * (len(filtered_data) // len(colors) + 1))[: len(filtered_data)]

    fig, ax = plt.subplots(figsize=(6.8, 5.5))
    positions = np.arange(1, len(filtered_data) + 1) * 1.0

    violin_alpha = 0.88
    parts = ax.violinplot(
        filtered_data,
        positions=positions,
        widths=0.7,
        showmeans=False,
        showmedians=False,
        showextrema=False,
    )
    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(colors[i])
        pc.set_edgecolor(None)
        pc.set_alpha(violin_alpha)

    for i, (d, pos) in enumerate(zip(filtered_data, positions)):
        if len(d) == 0:
            continue
        q1, median, q3 = np.percentile(d, [25, 50, 75])
        low, high = np.percentile(d, [5, 95])
        bar_color = "#6A6A6A"
        bar_lw = 6.0
        gap = 0.03 * (np.max(d) - np.min(d) + 1e-9)
        gap = min(gap, 0.35 * max(1e-9, q3 - q1))
        gap_low = float(median - gap / 2)
        gap_high = float(median + gap / 2)

        whisker_color = "#8A8A8A"
        whisker_lw = 1.1
        ax.plot(
            [pos, pos],
            [float(low), float(high)],
            color=whisker_color,
            linewidth=whisker_lw,
            zorder=2,
            solid_capstyle="butt",
        )

        try:
            from matplotlib.colors import to_rgba  # type: ignore

            bg = ax.get_facecolor()
            bg_rgb = (float(bg[0]), float(bg[1]), float(bg[2]))
            base = to_rgba(colors[i], 1.0)
            rgb = (float(base[0]), float(base[1]), float(base[2]))
            eff_rgb = tuple(violin_alpha * c + (1.0 - violin_alpha) * b for c, b in zip(rgb, bg_rgb))
            mask_color = (eff_rgb[0], eff_rgb[1], eff_rgb[2], 1.0)
        except Exception:
            mask_color = colors[i]

        d_span = float(np.max(d) - np.min(d) + 1e-9)
        eps = 0.01 * d_span
        ax.plot(
            [pos, pos],
            [gap_low - eps, gap_high + eps],
            color=mask_color,
            linewidth=whisker_lw + 3.6,
            zorder=2.6,
            solid_capstyle="butt",
        )

        lower_end = max(q1, median - gap / 2)
        upper_start = min(q3, median + gap / 2)
        if lower_end > q1:
            ax.plot([pos, pos], [q1, lower_end], color=bar_color, linewidth=bar_lw, solid_capstyle="butt", zorder=3)
        if q3 > upper_start:
            ax.plot([pos, pos], [upper_start, q3], color=bar_color, linewidth=bar_lw, solid_capstyle="butt", zorder=3)

    ax.set_xticks(positions)
    ax.set_xticklabels(labels, rotation=30, ha="right", color="black")
    _apply_nature_axes(ax, xlabel="", ylabel="Exam score")
    ax.set_xlim(0.4, float(len(filtered_data)) + 0.6)

    all_points = [x for sub in filtered_data for x in sub]
    span = None
    annotation_data_top = None
    if all_points:
        y_min, y_max = float(min(all_points)), float(max(all_points))
        span = max(1e-9, y_max - y_min)
        annotation_data_top = y_max
        y_bottom = max(0.0, y_min - 0.06 * span)
        y_top = y_max + 0.105 * span
        ax.set_ylim(y_bottom, y_top)

    ax.grid(False)

    try:
        scipy_stats = _try_import_stats()
        ctrl = filtered_data[0] if filtered_data else []
        if len(ctrl) >= 2:
            if span is None:
                span = 1.0

            pairs: List[Tuple[int, float]] = []
            for j in range(2, len(group_names) + 1):
                g = filtered_data[j - 1]
                if len(g) < 2:
                    continue
                group_label = group_names[j - 1]
                alt = (direction_by_group or {}).get(group_label)
                if alt not in {"greater", "less"}:
                    pairs = []
                    break
                try:
                    res = scipy_stats.brunnermunzel(g, ctrl, alternative=alt)
                except TypeError:
                    print("Brunner–Munzel one-sided not supported by this scipy; skip plot annotations.")
                    pairs = []
                    break
                p = float(res.pvalue)
                pairs.append((j, p))

            if all_points and pairs:
                p_bh = _bh_adjust([p for _j, p in pairs])
                for (j, p), p_adj in sorted(zip(pairs, p_bh), key=lambda t: t[0][0]):
                    adjusted_p_by_label[group_names[j - 1]] = float(p_adj)
    except Exception:
        pass

    def _sig_marker(p: Optional[float]) -> str:
        if p is None or math.isnan(p):
            return "ns"
        if p < 0.001:
            return "***"
        if p < 0.01:
            return "**"
        if p < 0.05:
            return "*"
        return "ns"

    y0, y1 = ax.get_ylim()
    y_span = max(1e-9, y1 - y0)
    if annotation_data_top is None:
        annotation_data_top = y1 - 0.105 * y_span
    y_sig = annotation_data_top + 0.083 * y_span
    y_mu = annotation_data_top + 0.040 * y_span
    for pos, mean_val, name in zip(positions, means, labels):
        if math.isnan(mean_val):
            continue
        marker = "" if name == "Control" else _sig_marker(adjusted_p_by_label.get(name))
        if marker:
            ax.text(
                pos,
                y_sig,
                marker,
                ha="center",
                va="center",
                fontsize=11,
                color="#111111",
                zorder=5,
            )
        ax.text(
            pos,
            y_mu,
            f"μ={mean_val:.2f}",
            ha="center",
            va="center",
            fontsize=11,
            color="#111111",
            zorder=5,
        )

    if PLOT_SHOW_N_IN_XTICK:
        try:
            from matplotlib.patches import Patch  # type: ignore

            legend_labels = [f"{name}: n={n}" for name, n in zip(labels, counts)]
            handles = [Patch(facecolor=c, edgecolor="none", label=lab) for c, lab in zip(colors, legend_labels)]
            ax.legend(
                handles=handles,
                loc="upper center",
                bbox_to_anchor=(0.5, -0.29),
                ncol=3,
                frameon=False,
                borderaxespad=0.0,
                fontsize=12,
                columnspacing=1.35,
                handlelength=1.6,
                handletextpad=0.6,
            )
            fig.tight_layout(rect=[0.0, 0.12, 1.0, 1.0])
        except Exception:
            fig.tight_layout()
    else:
        fig.tight_layout()

    if out_pdf is not None:
        out_pdf.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_pdf, bbox_inches="tight")
        print("Saved figure:", relative_path(out_pdf))

    if show:
        plt.show()
    plt.close(fig)


#%%
# =========================
# Block 3: Math A1 behavior analysis
# =========================
LABELS_PATH = _data_path("data/annotation/a1_chat_labels.json")
MATH_SCORES_PATH = _data_path("data/llm/math_score_reviews_with_answers.json", "data/annotation/math_score_reviews_with_answers.json")
VALID_USERS_PATH = REPO_ROOT / "data/processed/validuser_merged.csv"
EXCLUDE_USERS_PATH = REPO_ROOT / "data/processed/exclude_user.csv"

GROUP = "Experiment"
STAGE = "a1"
PROBLEM_PREFIX = "math_"

DROP_UNK_ASK = True
APPLY_EXCLUDE_USERS = True

PROBLEM_DENOM_POLICY = "attempted_or_chatted"
NOCHAT_TRIED_IF_ATTEMPTED = True

TARGET_PROBLEMS: Optional[List[str]] = None

TRIED_THRESHOLD = 0.5
COPY_FIRST_THRESHOLD = 0.5
PRETRY_BLANK_PROP_THRESHOLD = 0.8
PRECEDENCE = MATH_A1_PRECEDENCE

OUT_CSV: Optional[Path] = None

RUN_STATS = True
STATS_CATEGORIES: Tuple[str, ...] = (
    "no_chat",
    "mindless_copy",
    "challenge_wrong",
    "fix_after_wrong",
    "try_then_ask",
    "ask_then_explain",
)

PLOT_CONTROL_VS_EXP = True
FIG_OUT_PDF: Optional[Path] = REPO_ROOT / "figures/a1_math_hw2_control_vs_exp_behavior.pdf"
PLOT_SHOW_N_IN_XTICK = True

RUN_MATH_PLAGIARISM_EXTRA = True

RUN_LLM_ACCURACY_IMPACT = True
LLM_ACC_GROUP = "All"
LLM_DIFFICULTY_BINS = 3
FIG_LLM_ACC_PDF: Optional[Path] = REPO_ROOT / "figures/a1_math_llm_accuracy_by_difficulty.pdf"
FIG_LLM_WRONG_RATE_PDF: Optional[Path] = REPO_ROOT / "figures/a1_math_llm_wrong_outcome_by_difficulty.pdf"
FIG_LLM_CORRECT_NOT_ADOPTED_PDF: Optional[Path] = (
    REPO_ROOT / "figures/a1_math_llm_correct_not_adopted_by_difficulty.pdf"
)



@dataclass(frozen=True)
class ChatLabelMath:
    timestamp: float
    problem: str
    pre_tried: str
    ask_type: str
    ask_goal: str
    post_mode: str
    llm_wrong: bool
    post_has_correct: bool
    ask_blanks: Dict[str, Any]
    post_blanks: Dict[str, Any]
    pre_blanks: Dict[str, Any]


@dataclass
class UserFeaturesMath:
    user_id: str
    n_chats: int
    n_problems: int
    tried_rate: float
    mindless_copy_rate: float
    any_answer_copy_rate: float
    ask_then_explain: bool
    challenge_wrong: bool
    fix_after_wrong: bool
    verbatim_rate: float
    adapt_rate: float
    none_rate: float
    category: str
    hw2: Optional[float]


def load_math_group_map(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    out: Dict[str, str] = {}
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if not isinstance(row, dict):
                continue
            username = (row.get("账号") or row.get("username") or "").strip()
            course_raw = (row.get("课程") or row.get("course_raw") or "").strip()
            if not username or not course_raw:
                continue
            if "math" not in course_raw.lower():
                continue
            group = "Experiment" if "gpt" in course_raw.lower() else "Control"
            out[username] = group
    return out


def build_math_scores(*, group_map: Dict[str, str], excluded_users: set[str]) -> Dict[str, Dict[str, Any]]:
    computed = load_math_hw_scores(
        MATH_SCORES_PATH,
        hw1_problems=list(MATH_HW1_PROBLEMS_CFG),
        hw2_problems=list(MATH_HW2_PROBLEMS_CFG),
        score_map=dict(MATH_SCORE_MAP_CFG),
    )
    out: Dict[str, Dict[str, Any]] = {}
    for uid, s in computed.items():
        if uid in excluded_users:
            continue
        grp = group_map.get(uid)
        if grp is None:
            continue
        out[uid] = {
            "group": grp,
            "HW1": s.get("hw1_score", 0.0),
            "HW2": s.get("hw2_score", 0.0),
        }
    return out


def _pretry_rate_for_problem_math(problem_id: str, chats_in_problem: List[ChatLabelMath]) -> Optional[float]:
    try:
        blanks_map = MATH_SCORE_MAP_CFG.get(problem_id, {})
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


def build_user_problem_attempted_map_math(
    user_problem_chats: Dict[str, Dict[str, List[ChatLabelMath]]],
    details: Dict[str, Any],
) -> Dict[str, Dict[str, bool]]:
    out: Dict[str, Dict[str, bool]] = {}
    for uid, pmap in user_problem_chats.items():
        drec = details.get(uid, {}) if isinstance(details.get(uid, {}), dict) else {}
        amap: Dict[str, bool] = {}
        for p in pmap.keys():
            prec = drec.get(p, {})
            attempted = isinstance(prec, dict) and prec.get("user_answer") is not None
            amap[p] = bool(attempted)
        out[uid] = amap
    return out


def iter_labeled_math_chats(
    labels_by_user: Dict[str, Any],
    user_id: str,
    *,
    stage: str,
    problem_prefix: str,
    drop_unk_ask: bool,
) -> List[ChatLabelMath]:
    user_blob = labels_by_user.get(user_id, {})
    if not isinstance(user_blob, dict) or not user_blob:
        return []

    out: List[ChatLabelMath] = []
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

        ts = rec.get("timestamp")
        try:
            ts_f = float(ts)
        except Exception:
            ts_f = float("nan")

        out.append(
            ChatLabelMath(
                timestamp=ts_f,
                problem=problem,
                pre_tried=pre_tried,
                ask_type=ask_type,
                ask_goal=ask_goal,
                post_mode=post_mode,
                llm_wrong=llm_wrong,
                post_has_correct=post_has_correct,
                ask_blanks=ask_blanks if isinstance(ask_blanks, dict) else {},
                post_blanks=post_blanks if isinstance(post_blanks, dict) else {},
                pre_blanks=pre_blanks if isinstance(pre_blanks, dict) else {},
            )
        )

    out.sort(key=lambda x: (x.problem, x.timestamp))
    return out


def _compute_single_problem_features_math(
    seq: List[ChatLabelMath],
    *,
    problem_id: str,
    attempted_without_chat: bool,
    nochat_tried_if_attempted: bool,
    pretry_blank_prop_threshold: float,
) -> Dict[str, Any]:
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
    pretry_rate = _pretry_rate_for_problem_math(problem_id, seq)
    if not any_answer_request:
        tried_any = True
    elif pretry_rate is None:
        tried_any = any(c.pre_tried == LABEL_TRIED_Y for c in seq)
    else:
        tried_any = pretry_rate >= pretry_blank_prop_threshold
    any_post_verbatim = any(c.post_mode in VERBATIM_MODES for c in seq)

    seen_answer = False
    ask_then_explain = False
    for c in seq:
        is_explain = c.ask_goal in EXPLAIN_GOALS
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


def compute_problem_features_map_math(
    problem_chats: Dict[str, List[ChatLabelMath]],
    problem_attempted_without_chat: Dict[str, bool],
    *,
    nochat_tried_if_attempted: bool,
    pretry_blank_prop_threshold: float,
) -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for p, seq in problem_chats.items():
        out[p] = _compute_single_problem_features_math(
            seq,
            problem_id=p,
            attempted_without_chat=bool(problem_attempted_without_chat.get(p, False)),
            nochat_tried_if_attempted=nochat_tried_if_attempted,
            pretry_blank_prop_threshold=pretry_blank_prop_threshold,
        )
    return out


def build_user_problem_chats_math(
    labels: Dict[str, Any],
    scores: Dict[str, Any],
    details: Dict[str, Any],
    *,
    group: str,
    stage: str,
    problem_prefix: str,
    drop_unk_ask: bool,
    target_problems: List[str],
    problem_denom_policy: str,
    excluded_users: set[str],
) -> Dict[str, Dict[str, List[ChatLabelMath]]]:
    users = [
        uid
        for uid, s in scores.items()
        if isinstance(s, dict) and s.get("group") == group and uid not in excluded_users
    ]
    users.sort()

    out: Dict[str, Dict[str, List[ChatLabelMath]]] = {}
    for uid in users:
        chats = iter_labeled_math_chats(
            labels,
            uid,
            stage=stage,
            problem_prefix=problem_prefix,
            drop_unk_ask=drop_unk_ask,
        )
        by_prob: Dict[str, List[ChatLabelMath]] = defaultdict(list)
        for c in chats:
            by_prob[c.problem].append(c)

        drec = details.get(uid, {}) if isinstance(details.get(uid, {}), dict) else {}

        def _attempted(problem_id: str) -> bool:
            prec = drec.get(problem_id, {})
            return isinstance(prec, dict) and prec.get("user_answer") is not None

        included: Dict[str, List[ChatLabelMath]] = {}
        for p in target_problems:
            has_chat = p in by_prob and len(by_prob[p]) > 0
            attempted = _attempted(p)

            if problem_denom_policy == "chatted_only":
                if not has_chat:
                    continue
            elif problem_denom_policy == "attempted_or_chatted":
                if not (has_chat or attempted):
                    continue
            elif problem_denom_policy == "all_in_problem_set":
                pass
            else:
                raise ValueError(f"Unknown PROBLEM_DENOM_POLICY={problem_denom_policy!r}")

            included[p] = sorted(by_prob.get(p, []), key=lambda x: x.timestamp)

        out[uid] = included
    return out


def compute_single_user_features_math(
    user_id: str,
    problem_chats: Dict[str, List[ChatLabelMath]],
    problem_attempted_without_chat: Dict[str, bool],
    score_rec: Dict[str, Any],
    *,
    tried_threshold: float,
    copy_first_threshold: float,
    precedence: Tuple[str, ...],
    nochat_tried_if_attempted: bool,
) -> UserFeaturesMath:
    hw2 = safe_float(score_rec.get("HW2"))

    n_problems = len(problem_chats)
    n_chats = sum(len(v) for v in problem_chats.values())

    if n_problems == 0:
        tried_rate = 0.0
        mindless_copy_rate = 0.0
        any_answer_copy_rate = 0.0
        ask_then_explain = False
        challenge_wrong = False
        fix_after_wrong = False
        verbatim_rate = 0.0
        adapt_rate = 0.0
        none_rate = 0.0
    else:
        prob_feats = compute_problem_features_map_math(
            problem_chats,
            problem_attempted_without_chat,
            nochat_tried_if_attempted=nochat_tried_if_attempted,
            pretry_blank_prop_threshold=PRETRY_BLANK_PROP_THRESHOLD,
        )
        eligible = [f for f in prob_feats.values() if f.get("eligible_for_rates", True)]
        denom = len(eligible)
        if denom == 0:
            tried_rate = 0.0
            mindless_copy_rate = 0.0
            any_answer_copy_rate = 0.0
            ask_then_explain = False
        else:
            tried_rate = sum(1 for f in eligible if f["tried_any"]) / denom
            mindless_copy_rate = sum(1 for f in eligible if f["mindless_copy"]) / denom
            any_answer_copy_rate = sum(1 for f in eligible if f["any_answer_copy"]) / denom
            ask_then_explain = any(f["ask_then_explain"] for f in eligible)

        all_chats = [c for seq in problem_chats.values() for c in seq]
        if not all_chats:
            verbatim_rate = 0.0
            adapt_rate = 0.0
            none_rate = 0.0
            challenge_wrong = False
            fix_after_wrong = False
        else:
            verbatim_rate = sum(1 for c in all_chats if c.post_mode in VERBATIM_MODES) / len(all_chats)
            adapt_rate = sum(1 for c in all_chats if c.post_mode == "adapt") / len(all_chats)
            none_rate = sum(1 for c in all_chats if c.post_mode == "none") / len(all_chats)
            challenge_wrong = any((c.ask_type == "challenge" and c.llm_wrong) for c in all_chats)

            fix_after_wrong = False
            for seq in problem_chats.values():
                llm_correct: set[str] = set()
                llm_wrong: set[str] = set()
                post_correct: set[str] = set()
                pre_correct: set[str] = set()
                for c in seq:
                    c_ok, c_bad = _blanks_by_correct(c.ask_blanks)
                    llm_correct.update(c_ok)
                    llm_wrong.update(c_bad)
                    p_ok, _p_bad = _blanks_by_correct(c.post_blanks)
                    post_correct.update(p_ok)
                    pre_ok, _pre_bad = _blanks_by_correct(c.pre_blanks)
                    pre_correct.update(pre_ok)

                candidate = (llm_wrong - llm_correct) & post_correct & (set(post_correct) - pre_correct)
                if candidate:
                    fix_after_wrong = True
                    break

    category = _pick_math_category(
        n_chats=n_chats,
        tried_rate_problem=tried_rate,
        mindless_copy_rate_problem=mindless_copy_rate,
        ask_then_explain=ask_then_explain,
        challenge_wrong=challenge_wrong,
        fix_after_wrong=fix_after_wrong,
        tried_threshold=tried_threshold,
        copy_first_threshold=copy_first_threshold,
        precedence=precedence,
    )

    return UserFeaturesMath(
        user_id=user_id,
        n_chats=n_chats,
        n_problems=n_problems,
        tried_rate=tried_rate,
        mindless_copy_rate=mindless_copy_rate,
        any_answer_copy_rate=any_answer_copy_rate,
        ask_then_explain=ask_then_explain,
        challenge_wrong=challenge_wrong,
        fix_after_wrong=fix_after_wrong,
        verbatim_rate=verbatim_rate,
        adapt_rate=adapt_rate,
        none_rate=none_rate,
        category=category,
        hw2=hw2,
    )


def _pick_math_category(
    *,
    n_chats: int,
    tried_rate_problem: float,
    mindless_copy_rate_problem: float,
    ask_then_explain: bool,
    challenge_wrong: bool,
    fix_after_wrong: bool,
    tried_threshold: float = TRIED_THRESHOLD,
    copy_first_threshold: float = COPY_FIRST_THRESHOLD,
    precedence: Tuple[str, ...] = PRECEDENCE,
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


def compute_all_user_features_math(
    user_problem_chats: Dict[str, Dict[str, List[ChatLabelMath]]],
    user_problem_attempted_without_chat: Dict[str, Dict[str, bool]],
    scores: Dict[str, Any],
    *,
    tried_threshold: float,
    copy_first_threshold: float,
    precedence: Tuple[str, ...],
    nochat_tried_if_attempted: bool,
) -> Dict[str, UserFeaturesMath]:
    out: Dict[str, UserFeaturesMath] = {}
    for uid, pmap in user_problem_chats.items():
        score_rec = scores.get(uid, {}) if isinstance(scores.get(uid, {}), dict) else {}
        attempted_map = user_problem_attempted_without_chat.get(uid, {})
        out[uid] = compute_single_user_features_math(
            uid,
            pmap,
            attempted_map,
            score_rec,
            tried_threshold=tried_threshold,
            copy_first_threshold=copy_first_threshold,
            precedence=precedence,
            nochat_tried_if_attempted=nochat_tried_if_attempted,
        )
    return out


def user_features_to_rows_math(feats: List[UserFeaturesMath]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for f in feats:
        rows.append(
            {
                "user_id": f.user_id,
                "category": f.category,
                "n_chats": f.n_chats,
                "n_problems": f.n_problems,
                "tried_rate(problem)": f.tried_rate,
                "mindless_copy_rate(problem)": f.mindless_copy_rate,
                "any_answer_copy_rate(problem)": f.any_answer_copy_rate,
                "ask_then_explain": int(bool(f.ask_then_explain)),
                "challenge_wrong": int(bool(f.challenge_wrong)),
                "fix_after_wrong": int(bool(f.fix_after_wrong)),
                "verbatim_rate(chat)": f.verbatim_rate,
                "adapt_rate(chat)": f.adapt_rate,
                "none_rate(chat)": f.none_rate,
                "HW2": f.hw2,
            }
        )
    return rows


def _score_to_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        v = float(x)
    except Exception:
        return None
    if math.isnan(v):
        return None
    return v


def compute_problem_mean_scores(details: Dict[str, Any]) -> Dict[str, float]:
    by_problem: Dict[str, List[float]] = defaultdict(list)
    for _uid, urec in details.items():
        if not isinstance(urec, dict):
            continue
        for prob, prec in urec.items():
            if not isinstance(prec, dict):
                continue
            scores = prec.get("scores")
            if not isinstance(scores, dict) or not scores:
                continue
            weight_map = MATH_SCORE_MAP_CFG.get(prob, {})
            if not isinstance(weight_map, dict) or not weight_map:
                vals = [v for v in (_score_to_float(scores.get(k)) for k in scores.keys()) if v is not None]
                if vals:
                    by_problem[prob].append(float(statistics.mean(vals)))
                continue

            num = 0.0
            denom = 0.0
            for blank, w in weight_map.items():
                sv = _score_to_float(scores.get(blank))
                if sv is None:
                    continue
                try:
                    wv = float(w)
                except Exception:
                    continue
                num += wv * sv
                denom += abs(wv)
            if denom > 0:
                by_problem[prob].append(num / denom)
    out: Dict[str, float] = {}
    for prob, vals in by_problem.items():
        if vals:
            out[prob] = float(statistics.mean(vals))
    return out


def compute_blank_points_map() -> Dict[Tuple[str, str], float]:
    out: Dict[Tuple[str, str], float] = {}
    for prob, wmap in MATH_SCORE_MAP_CFG.items():
        if not isinstance(wmap, dict):
            continue
        for blank, w in wmap.items():
            try:
                out[(prob, str(blank))] = float(w)
            except Exception:
                continue
    return out


def assign_difficulty_bins(
    problem_mean_scores: Dict[str, float],
    *,
    n_bins: int,
) -> Tuple[Dict[str, str], List[float]]:
    if n_bins <= 1 or len(problem_mean_scores) == 0:
        return {p: "Medium" for p in problem_mean_scores.keys()}, []

    vals = sorted(problem_mean_scores.values())
    cuts = []
    for i in range(1, n_bins):
        q = i / n_bins
        k = (len(vals) - 1) * q
        f = int(math.floor(k))
        c = int(math.ceil(k))
        if f == c:
            cuts.append(vals[f])
        else:
            cuts.append(vals[f] + (vals[c] - vals[f]) * (k - f))

    def _label(score: float) -> str:
        if n_bins == 2:
            return "Hard" if score <= cuts[0] else "Easy"
        if n_bins == 3:
            if score <= cuts[0]:
                return "Hard"
            if score <= cuts[1]:
                return "Medium"
            return "Easy"
        idx = 0
        while idx < len(cuts) and score > cuts[idx]:
            idx += 1
        return f"Bin-{idx + 1}"

    out: Dict[str, str] = {}
    for p, s in problem_mean_scores.items():
        out[p] = _label(s)
    return out, cuts


def order_difficulty_bins(bins: List[str]) -> List[str]:
    preferred = ["Easy", "Medium", "Hard"]
    ordered = [b for b in preferred if b in bins]
    if len(ordered) == len(bins):
        return ordered
    tail = [b for b in sorted(bins) if b not in ordered]
    return ordered + tail


def assign_difficulty_thresholds(
    blank_points: Dict[Tuple[str, str], float],
    *,
    easy_max: float,
    medium_max: float,
) -> Dict[Tuple[str, str], str]:
    out: Dict[Tuple[str, str], str] = {}
    for key, pts in blank_points.items():
        if pts < easy_max:
            out[key] = "Easy"
        elif pts <= medium_max:
            out[key] = "Medium"
        else:
            out[key] = "Hard"
    return out


def _llm_correct_counts(ask_blanks: Any) -> Tuple[int, int]:
    if not isinstance(ask_blanks, dict):
        return 0, 0
    n_correct = 0
    n_total = 0
    for _k, v in ask_blanks.items():
        if not isinstance(v, dict):
            continue
        flag = _parse_correct_flag(v.get("correct"))
        if flag is None:
            continue
        n_total += 1
        if flag:
            n_correct += 1
    return n_correct, n_total


def _final_answer_correct(ask_blanks: Any, pre_blanks: Any, post_blanks: Any) -> Optional[bool]:
    merged: Dict[str, Any] = {}
    if isinstance(pre_blanks, dict):
        merged.update(pre_blanks)
    if isinstance(post_blanks, dict):
        merged.update(post_blanks)

    any_flag = False
    for _k, v in merged.items():
        if not isinstance(v, dict):
            continue
        flag = _parse_correct_flag(v.get("correct"))
        if flag is None:
            continue
        any_flag = True
        if not flag:
            return False
    if not any_flag:
        return None
    return True


def _final_blank_correct(pre_blanks: Any, post_blanks: Any, blank_id: str) -> Optional[bool]:
    merged: Dict[str, Any] = {}
    if isinstance(pre_blanks, dict):
        merged.update(pre_blanks)
    if isinstance(post_blanks, dict):
        merged.update(post_blanks)
    v = merged.get(blank_id)
    if not isinstance(v, dict):
        return None
    flag = _parse_correct_flag(v.get("correct"))
    return flag


def merge_final_blanks_across_chats(seq: List[ChatLabelMath]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    for c in seq:
        if isinstance(c.pre_blanks, dict):
            merged.update(c.pre_blanks)
        if isinstance(c.post_blanks, dict):
            merged.update(c.post_blanks)
    return merged


_PYTHON_BEHAVIOR_RUN_SOURCE = 'labels = load_json(LABELS_PATH)\nprint("Loading:", SCORES_PATH)\nscores = load_json(SCORES_PATH)\nprint("Loading:", DETAILS_PATH)\ndetails = load_json(DETAILS_PATH)\nprint("Loading:", EXCLUDE_USERS_PATH)\nexcluded_users = load_exclude_users(EXCLUDE_USERS_PATH) if APPLY_EXCLUDE_USERS else set()\n\nassert isinstance(labels, dict), f"labels must be dict, got {type(labels)}"\nassert isinstance(scores, dict), f"scores must be dict, got {type(scores)}"\nassert isinstance(details, dict), f"details must be dict, got {type(details)}"\n\nprint("\\nCONFIG:")\nprint("  GROUP =", GROUP)\nprint("  STAGE =", STAGE)\nprint("  PROBLEM_PREFIX =", PROBLEM_PREFIX)\nprint("  DROP_UNK_ASK =", DROP_UNK_ASK)\nprint("  APPLY_EXCLUDE_USERS =", APPLY_EXCLUDE_USERS)\nprint("  EXCLUDED_USERS(n) =", len(excluded_users))\nprint("  PROBLEM_DENOM_POLICY =", PROBLEM_DENOM_POLICY)\nprint("  NOCHAT_TRIED_IF_ATTEMPTED =", NOCHAT_TRIED_IF_ATTEMPTED)\nprint("  TRIED_THRESHOLD =", TRIED_THRESHOLD)\nprint("  COPY_FIRST_THRESHOLD =", COPY_FIRST_THRESHOLD)\nprint("  PRECEDENCE =", PRECEDENCE)\n\nif TARGET_PROBLEMS is None:\n    target_problems = infer_target_problems_from_labels(labels, stage=STAGE, problem_prefix=PROBLEM_PREFIX)\n    print("\\nInferred TARGET_PROBLEMS from labels:", len(target_problems))\n    for p in target_problems:\n        print(" ", p)\nelse:\n    target_problems = list(TARGET_PROBLEMS)\n    print("\\nUsing explicit TARGET_PROBLEMS:", len(target_problems))\n\nuser_problem_chats = build_user_problem_chats(\n    labels,\n    scores,\n    details,\n    group=GROUP,\n    stage=STAGE,\n    problem_prefix=PROBLEM_PREFIX,\n    drop_unk_ask=DROP_UNK_ASK,\n    target_problems=target_problems,\n    problem_denom_policy=PROBLEM_DENOM_POLICY,\n    excluded_users=excluded_users,\n)\n\nuser_problem_attempted_without_chat = build_user_problem_attempted_map(user_problem_chats, details)\n\nuser_features_by_id = compute_all_user_features(\n    user_problem_chats,\n    user_problem_attempted_without_chat,\n    scores,\n    tried_threshold=TRIED_THRESHOLD,\n    copy_first_threshold=COPY_FIRST_THRESHOLD,\n    precedence=PRECEDENCE,\n    nochat_tried_if_attempted=NOCHAT_TRIED_IF_ATTEMPTED,\n)\n\nfeats = list(user_features_by_id.values())\n\nprint("\\nUsers in group:", len(feats))\nprint("Users with >=1 labeled chat:", sum(1 for f in feats if f.n_chats > 0))\nprint("Category counts:", dict(Counter(f.category for f in feats)))\n\ndef _problem_features_for_heterogeneity_py(\n    seq: List[ChatLabel], problem_id: str, attempted_without_chat: bool\n) -> Dict[str, Any]:\n    return compute_single_problem_features(\n        seq,\n        attempted_without_chat=attempted_without_chat,\n        nochat_tried_if_attempted=NOCHAT_TRIED_IF_ATTEMPTED,\n    )\n\nif SAVE_SINGLE_BEHAVIOR_HETEROGENEITY:\n    _plot_behavior_heterogeneity_heatmap(\n        user_problem_chats=user_problem_chats,\n        user_problem_attempted_without_chat=user_problem_attempted_without_chat,\n        target_problems=target_problems,\n        problem_features_fn=_problem_features_for_heterogeneity_py,\n        out_pdf=FIGURES_DIR / "a1_behavior_heterogeneity_heatmap_python.pdf",\n        course_label="Python",\n        show=SHOW_FIGURES,\n    )\n\nprint("\\nIncluded problems per user (by policy):")\nprint("  mean_n_problems =", statistics.mean([f.n_problems for f in feats]) if feats else 0.0)\nprint("  min_n_problems  =", min([f.n_problems for f in feats]) if feats else 0)\nprint("  max_n_problems  =", max([f.n_problems for f in feats]) if feats else 0)\n\nprint("\\nProblems solved/attempted WITHOUT chat (estimated via python_details.user_answer != None):")\nrows = []\nfor uid, pmap in user_problem_chats.items():\n    amap = user_problem_attempted_without_chat.get(uid, {})\n    n_nochat_attempted = sum(1 for p, seq in pmap.items() if (len(seq) == 0 and amap.get(p, False)))\n    n_chatted = sum(1 for _p, seq in pmap.items() if len(seq) > 0)\n    rows.append((uid, n_nochat_attempted, n_chatted, len(pmap)))\n\nvals = [r[1] for r in rows]\nprint("  mean_nochat_attempted =", statistics.mean(vals) if vals else 0.0)\nprint("  median_nochat_attempted =", statistics.median(vals) if vals else 0.0)\nprint("  max_nochat_attempted =", max(vals) if vals else 0)\nprint("  Example top users (uid, n_nochat_attempted, n_chatted, n_problems):")\nfor r in sorted(rows, key=lambda x: (-x[1], x[2], x[0]))[:10]:\n    print("   ", r)\n\nby_cat: Dict[str, List[UserFeatures]] = defaultdict(list)\nfor f in feats:\n    by_cat[f.category].append(f)\n\ncat_order = ["no_chat", "mindless_copy", "try_then_ask", "ask_then_explain", "other"]\ncat_order = [c for c in cat_order if c in by_cat] + [c for c in sorted(by_cat.keys()) if c not in cat_order]\n\n\ndef _fmt(x: Optional[float]) -> str:\n    if x is None:\n        return "NA"\n    return f"{x:.4f}"\n\n\nprint("\\nPer-category HW2 summary (raw):")\nprint("\\t".join(["category", "n", "HW2_mean", "HW2_median", "HW2_std"]))\nfor cat in cat_order:\n    rows = by_cat.get(cat, [])\n    hw2_vals = [f.hw2 for f in rows if f.hw2 is not None]\n    s1 = summarize(hw2_vals)  # type: ignore[arg-type]\n    print(\n        "\\t".join(\n            [\n                cat,\n                str(len(rows)),\n                _fmt(s1["mean"]),\n                _fmt(s1["median"]),\n                _fmt(s1["std"]),\n            ]\n        )\n    )\n\nprint("\\nPer-category behavior summary (mean rates):")\nprint(\n    "\\t".join(\n        [\n            "category",\n            "n",\n            "mean_n_chats",\n            "mean_n_problems",\n            "mean_tried_rate(problem)",\n            "mean_mindless_copy_rate(problem)",\n            "mean_any_answer_copy_rate(problem)",\n            "mean_verbatim_rate(chat)",\n            "mean_adapt_rate(chat)",\n            "mean_none_rate(chat)",\n            "ask_then_explain_count",\n        ]\n    )\n)\n\nfor cat in cat_order:\n    rows = by_cat.get(cat, [])\n    if not rows:\n        continue\n    mean_n = statistics.mean([f.n_chats for f in rows])\n    mean_np = statistics.mean([f.n_problems for f in rows])\n    mean_tr = statistics.mean([f.tried_rate for f in rows])\n    mean_cf = statistics.mean([f.mindless_copy_rate for f in rows])\n    mean_ac = statistics.mean([f.any_answer_copy_rate for f in rows])\n    mean_vb = statistics.mean([f.verbatim_rate for f in rows])\n    mean_ad = statistics.mean([f.adapt_rate for f in rows])\n    mean_no = statistics.mean([f.none_rate for f in rows])\n    n_explain = sum(1 for f in rows if f.ask_then_explain)\n    print(\n        "\\t".join(\n            [\n                cat,\n                str(len(rows)),\n                f"{mean_n:.2f}",\n                f"{mean_np:.2f}",\n                f"{mean_tr:.3f}",\n                f"{mean_cf:.3f}",\n                f"{mean_ac:.3f}",\n                f"{mean_vb:.3f}",\n                f"{mean_ad:.3f}",\n                f"{mean_no:.3f}",\n                str(n_explain),\n            ]\n        )\n    )\n\nif not PLOT_CONTROL_VS_EXP:\n    print("\\nPLOT_CONTROL_VS_EXP is False; skip figure.")\nelse:\n    control_hw2: List[float] = []\n    for uid, srec in scores.items():\n        if not isinstance(srec, dict):\n            continue\n        if APPLY_EXCLUDE_USERS and uid in excluded_users:\n            continue\n        if srec.get("group") != "Control":\n            continue\n        v = safe_float(srec.get("HW2"))\n        if v is not None:\n            control_hw2.append(v)\n\n    if GROUP == "Experiment":\n        exp_feats = feats\n    else:\n        exp_user_problem_chats = build_user_problem_chats(\n            labels,\n            scores,\n            details,\n            group="Experiment",\n            stage=STAGE,\n            problem_prefix=PROBLEM_PREFIX,\n            drop_unk_ask=DROP_UNK_ASK,\n            target_problems=target_problems,\n            problem_denom_policy=PROBLEM_DENOM_POLICY,\n            excluded_users=excluded_users,\n        )\n        exp_attempted_map = build_user_problem_attempted_map(exp_user_problem_chats, details)\n        exp_features_by_id = compute_all_user_features(\n            exp_user_problem_chats,\n            exp_attempted_map,\n            scores,\n            tried_threshold=TRIED_THRESHOLD,\n            copy_first_threshold=COPY_FIRST_THRESHOLD,\n            precedence=PRECEDENCE,\n            nochat_tried_if_attempted=NOCHAT_TRIED_IF_ATTEMPTED,\n        )\n        exp_feats = list(exp_features_by_id.values())\n\n    behavior_order = ["no_chat", "mindless_copy", "try_then_ask", "ask_then_explain"]\n    display_name = {\n        "no_chat": "Abstention",\n        "mindless_copy": "Rote-adoption",\n        "try_then_ask": "Active-trial",\n        "ask_then_explain": "Verification",\n    }\n    direction_by_group = {\n        display_name["no_chat"]: "less",\n        display_name["mindless_copy"]: "less",\n        display_name["try_then_ask"]: "greater",\n        display_name["ask_then_explain"]: "greater",\n    }\n\n    exp_hw2_by_behavior: Dict[str, List[float]] = {}\n    for cat in behavior_order:\n        ys = [f.hw2 for f in exp_feats if f.category == cat and f.hw2 is not None]\n        exp_hw2_by_behavior[display_name[cat]] = [float(x) for x in ys]  # type: ignore[arg-type]\n\n    print("\\nFigure data counts (HW2 raw):")\n    print("  Control n =", len(control_hw2))\n    for k, ys in exp_hw2_by_behavior.items():\n        print(f"  {k} n = {len(ys)}")\n\n    print_control_vs_exp_tests(\n        control_hw2=control_hw2,\n        exp_hw2_by_behavior=exp_hw2_by_behavior,\n        direction_by_group=direction_by_group,\n    )\n\n    exp_hw2_by_behavior = {k: ys for k, ys in exp_hw2_by_behavior.items() if len(ys) > 0}\n    if len(control_hw2) == 0 or len(exp_hw2_by_behavior) == 0:\n        print("  Not enough data to plot.")\n    else:\n        plot_control_vs_exp_behaviors_hw2(\n            control_hw2=control_hw2,\n            exp_hw2_by_behavior=exp_hw2_by_behavior,\n            exp_label_to_color={\n                display_name["try_then_ask"]: "#a1d99b",\n                display_name["ask_then_explain"]: "#31a354",\n            },\n            out_pdf=FIG_OUT_PDF,\n            show=SHOW_FIGURES,\n            direction_by_group=direction_by_group,\n        )\n\nif RUN_PY_PLAGIARISM_EXTRA:\n    def _problem_features_py(seq: List[ChatLabel], problem_id: str, attempted_without_chat: bool) -> Dict[str, Any]:\n        return compute_single_problem_features(\n            seq,\n            attempted_without_chat=attempted_without_chat,\n            nochat_tried_if_attempted=NOCHAT_TRIED_IF_ATTEMPTED,\n        )\n\n    run_plagiarism_extra_analyses(\n        label="Python",\n        feats=feats,\n        user_problem_chats=user_problem_chats,\n        details=details,\n        target_problems=target_problems,\n        group_name=GROUP,\n        problem_features_fn=_problem_features_py,\n        behaviors_db_path=REPO_ROOT / "data/processed/behaviors/merged_behaviors.db",\n        hw1_entry_stage_name="完成作业 1",\n        output_prefix="a1",\n        figures_dir=FIGURES_DIR,\n        show=SHOW_FIGURES,\n        active_trial_threshold=TRIED_THRESHOLD,\n        include_problem_and_cdf_figures=False,\n    )\n\nif OUT_CSV is None:\n    print("\\nOUT_CSV is None; skip writing CSV.")\nelse:\n    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)\n    rows = user_features_to_rows(feats)\n    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:\n        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])\n        w.writeheader()\n        w.writerows(rows)\n    print("\\nWrote CSV:", OUT_CSV)\n\nif not RUN_STATS:\n    print("\\nRUN_STATS is False; skip stats.")\nelse:\n    try:\n        hw2_by = {c: [f.hw2 for f in rows if f.hw2 is not None] for c, rows in by_cat.items()}\n        run_nonparametric_tests(hw2_by, categories=STATS_CATEGORIES, label="HW2 (raw)")\n    except Exception as e:\n        print("\\nStats failed:", type(e).__name__, str(e))\n\n# LLM Accuracy by Difficulty (Python)\nif not RUN_PY_LLM_ACCURACY:\n    print("\\nRUN_PY_LLM_ACCURACY is False; skip LLM accuracy analysis.")\nelse:\n    print("\\n[LLM Accuracy by Difficulty] Start (Python)")\n\n    if PY_LLM_ACC_GROUP not in {"All", "Experiment", "Control"}:\n        raise ValueError(f"PY_LLM_ACC_GROUP must be All/Experiment/Control, got {PY_LLM_ACC_GROUP!r}")\n\n    if PY_LLM_ACC_GROUP == "All":\n        analysis_user_ids = [uid for uid in scores.keys() if uid not in excluded_users]\n    else:\n        analysis_user_ids = [\n            uid\n            for uid, s in scores.items()\n            if isinstance(s, dict) and s.get("group") == PY_LLM_ACC_GROUP and uid not in excluded_users\n        ]\n\n    problem_max_score: Dict[str, int] = {}\n    for _uid, drec in details.items():\n        if not isinstance(drec, dict):\n            continue\n        probs = drec.get("problems", {}) if isinstance(drec.get("problems", {}), dict) else {}\n        for p, prec in probs.items():\n            if not isinstance(prec, dict):\n                continue\n            ms = prec.get("max_score")\n            if ms is None:\n                continue\n            try:\n                ms_i = int(ms)\n            except Exception:\n                continue\n            if p not in problem_max_score:\n                problem_max_score[p] = ms_i\n\n    def _difficulty(ms: Optional[int]) -> Optional[str]:\n        if ms is None:\n            return None\n        if ms in (1, 2):\n            return "Easy"\n        if ms == 3:\n            return "Medium"\n        if ms in (4, 5):\n            return "Hard"\n        return None\n\n    diff_bins = ["Easy", "Medium", "Hard"]\n    counts_by_diff: Dict[str, Tuple[int, int]] = {b: (0, 0) for b in diff_bins}\n\n    for uid in analysis_user_ids:\n        chats = iter_labeled_py_chats(\n            labels,\n            uid,\n            stage=STAGE,\n            problem_prefix=PROBLEM_PREFIX,\n            drop_unk_ask=DROP_UNK_ASK,\n        )\n        for c in chats:\n            if c.ask_correct is None:\n                continue\n            ms = problem_max_score.get(c.problem)\n            d = _difficulty(ms)\n            if d is None:\n                continue\n            k, n = counts_by_diff[d]\n            counts_by_diff[d] = (k + (1 if c.ask_correct else 0), n + 1)\n\n    print("\\nLLM Accuracy by Difficulty (Python, problem-level):")\n    print("  group =", PY_LLM_ACC_GROUP)\n    print("\\t".join(["difficulty", "n_correct", "n_total", "accuracy", "wilson_95%_ci"]))\n    for b in diff_bins:\n        k, n = counts_by_diff.get(b, (0, 0))\n        acc = (k / n) if n else float("nan")\n        lo, hi = wilson_ci(k, n)\n        print("\\t".join([b, str(k), str(n), f"{acc:.3f}", f"[{lo:.3f}, {hi:.3f}]"]))\n\n    plt3 = _maybe_import_matplotlib()\n    if plt3 is None:\n        print("\\nLLM accuracy plot skipped (missing dependency: matplotlib). Install with: `uv add matplotlib`")\n    else:\n        _set_nature_style_v2()\n        import numpy as np  # type: ignore\n\n        fig, ax = plt3.subplots(figsize=(3.6, 3.2))\n        x = np.arange(len(diff_bins))\n        acc_vals = []\n        err_low = []\n        err_high = []\n        n_totals = []\n        for b in diff_bins:\n            k, n = counts_by_diff.get(b, (0, 0))\n            n_totals.append(n)\n            acc = (k / n) if n else 0.0\n            lo, hi = wilson_ci(k, n)\n            acc_vals.append(acc)\n            err_low.append(acc - lo)\n            err_high.append(hi - acc)\n\n        bar_color = "#9ecae1"\n        ax.bar(x, acc_vals, color=bar_color, edgecolor="white", linewidth=0.8)\n        ax.errorbar(x, acc_vals, yerr=[err_low, err_high], fmt="none", ecolor="#2b2b2b", capsize=3, lw=1.0)\n        ax.set_xticks(x)\n        ax.set_xticklabels(diff_bins)\n        ax.set_ylim(0.0, 1.0)\n        _apply_nature_axes(ax, xlabel="Difficulty", ylabel="Accuracy")\n\n        fig.tight_layout()\n        if FIG_PY_LLM_ACC_PDF is not None:\n            FIG_PY_LLM_ACC_PDF.parent.mkdir(parents=True, exist_ok=True)\n            fig.savefig(FIG_PY_LLM_ACC_PDF, dpi=300, bbox_inches="tight")\n            print("Saved:", FIG_PY_LLM_ACC_PDF)\n        if SHOW_FIGURES:\n            plt3.show()\n        plt3.close(fig)\n'
_MATH_BEHAVIOR_RUN_SOURCE = 'labels = load_json(LABELS_PATH)\nprint("Loading:", MATH_SCORES_PATH)\nmath_raw = load_json(MATH_SCORES_PATH)\nprint("Loading:", VALID_USERS_PATH)\ngroup_map = load_math_group_map(VALID_USERS_PATH)\nprint("Loading:", EXCLUDE_USERS_PATH)\nexcluded_users = load_exclude_users(EXCLUDE_USERS_PATH) if APPLY_EXCLUDE_USERS else set()\n\nscores = build_math_scores(\n    group_map=group_map,\n    excluded_users=excluded_users,\n)\ndetails = math_raw\n\nassert isinstance(labels, dict), f"labels must be dict, got {type(labels)}"\nassert isinstance(scores, dict), f"scores must be dict, got {type(scores)}"\nassert isinstance(details, dict), f"details must be dict, got {type(details)}"\n\nprint("\\nCONFIG:")\nprint("  GROUP =", GROUP)\nprint("  STAGE =", STAGE)\nprint("  PROBLEM_PREFIX =", PROBLEM_PREFIX)\nprint("  DROP_UNK_ASK =", DROP_UNK_ASK)\nprint("  APPLY_EXCLUDE_USERS =", APPLY_EXCLUDE_USERS)\nprint("  EXCLUDED_USERS(n) =", len(excluded_users))\nprint("  PROBLEM_DENOM_POLICY =", PROBLEM_DENOM_POLICY)\nprint("  NOCHAT_TRIED_IF_ATTEMPTED =", NOCHAT_TRIED_IF_ATTEMPTED)\nprint("  TRIED_THRESHOLD =", TRIED_THRESHOLD)\nprint("  COPY_FIRST_THRESHOLD =", COPY_FIRST_THRESHOLD)\nprint("  PRETRY_BLANK_PROP_THRESHOLD =", PRETRY_BLANK_PROP_THRESHOLD)\nprint("  PRECEDENCE =", PRECEDENCE)\n\nif TARGET_PROBLEMS is None:\n    target_problems = infer_target_problems_from_labels(labels, stage=STAGE, problem_prefix=PROBLEM_PREFIX)\n    print("\\nInferred TARGET_PROBLEMS from labels:", len(target_problems))\n    for p in target_problems:\n        print(" ", p)\nelse:\n    target_problems = list(TARGET_PROBLEMS)\n    print("\\nUsing explicit TARGET_PROBLEMS:", len(target_problems))\n\nuser_problem_chats = build_user_problem_chats_math(\n    labels,\n    scores,\n    details,\n    group=GROUP,\n    stage=STAGE,\n    problem_prefix=PROBLEM_PREFIX,\n    drop_unk_ask=DROP_UNK_ASK,\n    target_problems=target_problems,\n    problem_denom_policy=PROBLEM_DENOM_POLICY,\n    excluded_users=excluded_users,\n)\n\nuser_problem_attempted_without_chat = build_user_problem_attempted_map_math(user_problem_chats, details)\n\nuser_features_by_id = compute_all_user_features_math(\n    user_problem_chats,\n    user_problem_attempted_without_chat,\n    scores,\n    tried_threshold=TRIED_THRESHOLD,\n    copy_first_threshold=COPY_FIRST_THRESHOLD,\n    precedence=PRECEDENCE,\n    nochat_tried_if_attempted=NOCHAT_TRIED_IF_ATTEMPTED,\n)\n\nfeats = list(user_features_by_id.values())\n\nprint("\\nUsers in group:", len(feats))\nprint("Users with >=1 labeled chat:", sum(1 for f in feats if f.n_chats > 0))\nprint("Category counts:", dict(Counter(f.category for f in feats)))\n\ndef _problem_features_for_heterogeneity_math(\n    seq: List[ChatLabelMath], problem_id: str, attempted_without_chat: bool\n) -> Dict[str, Any]:\n    pf = _compute_single_problem_features_math(\n        seq,\n        problem_id=problem_id,\n        attempted_without_chat=attempted_without_chat,\n        nochat_tried_if_attempted=NOCHAT_TRIED_IF_ATTEMPTED,\n        pretry_blank_prop_threshold=PRETRY_BLANK_PROP_THRESHOLD,\n    )\n    challenge_wrong = any((c.ask_type == "challenge" and c.llm_wrong) for c in seq)\n    fix_after_wrong = False\n    llm_correct: set[str] = set()\n    llm_wrong: set[str] = set()\n    post_correct: set[str] = set()\n    pre_correct: set[str] = set()\n    for c in seq:\n        c_ok, c_bad = _blanks_by_correct(c.ask_blanks)\n        llm_correct.update(c_ok)\n        llm_wrong.update(c_bad)\n        p_ok, _p_bad = _blanks_by_correct(c.post_blanks)\n        post_correct.update(p_ok)\n        pre_ok, _pre_bad = _blanks_by_correct(c.pre_blanks)\n        pre_correct.update(pre_ok)\n    candidate = (llm_wrong - llm_correct) & post_correct & (set(post_correct) - pre_correct)\n    if candidate:\n        fix_after_wrong = True\n    pf["challenge_wrong"] = bool(challenge_wrong)\n    pf["fix_after_wrong"] = bool(fix_after_wrong)\n    return pf\n\n# Twin-panel (Python + Game Theory) behavior heterogeneity figure\npy_scores_twin = load_json(REPO_ROOT / "data/annotation/python_scores.json")\npy_details_twin = load_json(REPO_ROOT / "data/annotation/python_details.json")\npy_target_twin = infer_target_problems_from_labels(labels, stage="a1", problem_prefix="py_")\npy_user_problem_chats_twin = build_user_problem_chats(\n    labels,\n    py_scores_twin,\n    py_details_twin,\n    group="Experiment",\n    stage="a1",\n    problem_prefix="py_",\n    drop_unk_ask=True,\n    target_problems=py_target_twin,\n    problem_denom_policy="attempted_or_chatted",\n    excluded_users=excluded_users,\n)\npy_attempted_twin = build_user_problem_attempted_map(py_user_problem_chats_twin, py_details_twin)\n\ndef _problem_features_for_heterogeneity_py_twin(\n    seq: List[ChatLabel], problem_id: str, attempted_without_chat: bool\n) -> Dict[str, Any]:\n    return compute_single_problem_features(\n        seq,\n        attempted_without_chat=attempted_without_chat,\n        nochat_tried_if_attempted=NOCHAT_TRIED_IF_ATTEMPTED,\n    )\n\n_plot_behavior_heterogeneity_two_panel(\n    py_user_problem_chats=py_user_problem_chats_twin,\n    py_user_problem_attempted_without_chat=py_attempted_twin,\n    py_target_problems=py_target_twin,\n    py_problem_features_fn=_problem_features_for_heterogeneity_py_twin,\n    math_user_problem_chats=user_problem_chats,\n    math_user_problem_attempted_without_chat=user_problem_attempted_without_chat,\n    math_target_problems=target_problems,\n    math_problem_features_fn=_problem_features_for_heterogeneity_math,\n    out_pdf=FIGURES_DIR / "a1_behavior_heterogeneity_twin_python_game_theory.pdf",\n    show=SHOW_FIGURES,\n)\n\nif SAVE_SINGLE_BEHAVIOR_HETEROGENEITY:\n    _plot_behavior_heterogeneity_heatmap(\n        user_problem_chats=user_problem_chats,\n        user_problem_attempted_without_chat=user_problem_attempted_without_chat,\n        target_problems=target_problems,\n        problem_features_fn=_problem_features_for_heterogeneity_math,\n        out_pdf=FIGURES_DIR / "a1_behavior_heterogeneity_heatmap_game_theory.pdf",\n        course_label="Game Theory",\n        show=SHOW_FIGURES,\n    )\n\nprint("\\nIncluded problems per user (by policy):")\nprint("  mean_n_problems =", statistics.mean([f.n_problems for f in feats]) if feats else 0.0)\nprint("  min_n_problems  =", min([f.n_problems for f in feats]) if feats else 0)\nprint("  max_n_problems  =", max([f.n_problems for f in feats]) if feats else 0)\n\nprint("\\nProblems solved/attempted WITHOUT chat (estimated via math_score_reviews_with_answers.user_answer != None):")\nrows = []\nfor uid, pmap in user_problem_chats.items():\n    amap = user_problem_attempted_without_chat.get(uid, {})\n    n_nochat_attempted = sum(1 for p, seq in pmap.items() if (len(seq) == 0 and amap.get(p, False)))\n    n_chatted = sum(1 for _p, seq in pmap.items() if len(seq) > 0)\n    rows.append((uid, n_nochat_attempted, n_chatted, len(pmap)))\n\nvals = [r[1] for r in rows]\nprint("  mean_nochat_attempted =", statistics.mean(vals) if vals else 0.0)\nprint("  median_nochat_attempted =", statistics.median(vals) if vals else 0.0)\nprint("  max_nochat_attempted =", max(vals) if vals else 0)\nprint("  Example top users (uid, n_nochat_attempted, n_chatted, n_problems):")\nfor r in sorted(rows, key=lambda x: (-x[1], x[2], x[0]))[:10]:\n    print("   ", r)\n\nby_cat: Dict[str, List[UserFeaturesMath]] = defaultdict(list)\nfor f in feats:\n    by_cat[f.category].append(f)\n\ncat_order = [\n    "no_chat",\n    "mindless_copy",\n    "challenge_wrong",\n    "fix_after_wrong",\n    "try_then_ask",\n    "ask_then_explain",\n    "other",\n]\ncat_order = [c for c in cat_order if c in by_cat] + [c for c in sorted(by_cat.keys()) if c not in cat_order]\n\n\ndef _fmt_math(x: Optional[float]) -> str:\n    if x is None:\n        return "NA"\n    return f"{x:.4f}"\n\n\nprint("\\nPer-category HW2 summary (raw):")\nprint("\\t".join(["category", "n", "HW2_mean", "HW2_median", "HW2_std"]))\nfor cat in cat_order:\n    rows = by_cat.get(cat, [])\n    hw2_vals = [f.hw2 for f in rows if f.hw2 is not None]\n    s1 = summarize(hw2_vals)  # type: ignore[arg-type]\n    print(\n        "\\t".join(\n            [\n                cat,\n                str(len(rows)),\n                _fmt_math(s1["mean"]),\n                _fmt_math(s1["median"]),\n                _fmt_math(s1["std"]),\n            ]\n        )\n    )\n\nprint("\\nPer-category behavior summary (mean rates):")\nprint(\n    "\\t".join(\n        [\n            "category",\n            "n",\n            "mean_n_chats",\n            "mean_n_problems",\n            "mean_tried_rate(problem)",\n            "mean_mindless_copy_rate(problem)",\n            "mean_any_answer_copy_rate(problem)",\n            "mean_verbatim_rate(chat)",\n            "mean_adapt_rate(chat)",\n            "mean_none_rate(chat)",\n            "challenge_wrong_count",\n            "fix_after_wrong_count",\n            "ask_then_explain_count",\n        ]\n    )\n)\n\nfor cat in cat_order:\n    rows = by_cat.get(cat, [])\n    if not rows:\n        continue\n    mean_n = statistics.mean([f.n_chats for f in rows])\n    mean_np = statistics.mean([f.n_problems for f in rows])\n    mean_tr = statistics.mean([f.tried_rate for f in rows])\n    mean_cf = statistics.mean([f.mindless_copy_rate for f in rows])\n    mean_ac = statistics.mean([f.any_answer_copy_rate for f in rows])\n    mean_vb = statistics.mean([f.verbatim_rate for f in rows])\n    mean_ad = statistics.mean([f.adapt_rate for f in rows])\n    mean_no = statistics.mean([f.none_rate for f in rows])\n    n_challenge_wrong = sum(1 for f in rows if f.challenge_wrong)\n    n_fix_after_wrong = sum(1 for f in rows if f.fix_after_wrong)\n    n_explain = sum(1 for f in rows if f.ask_then_explain)\n    print(\n        "\\t".join(\n            [\n                cat,\n                str(len(rows)),\n                f"{mean_n:.2f}",\n                f"{mean_np:.2f}",\n                f"{mean_tr:.3f}",\n                f"{mean_cf:.3f}",\n                f"{mean_ac:.3f}",\n                f"{mean_vb:.3f}",\n                f"{mean_ad:.3f}",\n                f"{mean_no:.3f}",\n                str(n_challenge_wrong),\n                str(n_fix_after_wrong),\n                str(n_explain),\n            ]\n        )\n    )\n\nif not PLOT_CONTROL_VS_EXP:\n    print("\\nPLOT_CONTROL_VS_EXP is False; skip figure.")\nelse:\n    control_hw2: List[float] = []\n    for uid, srec in scores.items():\n        if not isinstance(srec, dict):\n            continue\n        if APPLY_EXCLUDE_USERS and uid in excluded_users:\n            continue\n        if srec.get("group") != "Control":\n            continue\n        v = safe_float(srec.get("HW2"))\n        if v is not None:\n            control_hw2.append(v)\n\n    if GROUP == "Experiment":\n        exp_feats = feats\n    else:\n        exp_user_problem_chats = build_user_problem_chats_math(\n            labels,\n            scores,\n            details,\n            group="Experiment",\n            stage=STAGE,\n            problem_prefix=PROBLEM_PREFIX,\n            drop_unk_ask=DROP_UNK_ASK,\n            target_problems=target_problems,\n            problem_denom_policy=PROBLEM_DENOM_POLICY,\n            excluded_users=excluded_users,\n        )\n        exp_attempted_map = build_user_problem_attempted_map_math(exp_user_problem_chats, details)\n        exp_features_by_id = compute_all_user_features_math(\n            exp_user_problem_chats,\n            exp_attempted_map,\n            scores,\n            tried_threshold=TRIED_THRESHOLD,\n            copy_first_threshold=COPY_FIRST_THRESHOLD,\n            precedence=PRECEDENCE,\n            nochat_tried_if_attempted=NOCHAT_TRIED_IF_ATTEMPTED,\n        )\n        exp_feats = list(exp_features_by_id.values())\n\n    behavior_order = [\n        "no_chat",\n        "mindless_copy",\n        "try_then_ask",\n        "fix_after_wrong",\n        "challenge_wrong",\n        "ask_then_explain",\n    ]\n    display_name = {\n        "no_chat": "Abstention",\n        "mindless_copy": "Rote-adoption",\n        "challenge_wrong": "Verification",\n        "fix_after_wrong": "Error-correction",\n        "try_then_ask": "Active-trial",\n        "ask_then_explain": "Verification",\n    }\n    direction_by_group = {\n        display_name["no_chat"]: "less",\n        display_name["mindless_copy"]: "less",\n        display_name["try_then_ask"]: "greater",\n        display_name["fix_after_wrong"]: "greater",\n        display_name["challenge_wrong"]: "greater",\n        display_name["ask_then_explain"]: "greater",\n    }\n\n    exp_hw2_by_behavior: Dict[str, List[float]] = {}\n    for cat in behavior_order:\n        ys = [f.hw2 for f in exp_feats if f.category == cat and f.hw2 is not None]\n        label = display_name[cat]\n        exp_hw2_by_behavior.setdefault(label, []).extend(float(x) for x in ys)  # type: ignore[arg-type]\n\n    print("\\nFigure data counts (HW2 raw):")\n    print("  Control n =", len(control_hw2))\n    for k, ys in exp_hw2_by_behavior.items():\n        print(f"  {k} n = {len(ys)}")\n\n    print_control_vs_exp_tests(\n        control_hw2=control_hw2,\n        exp_hw2_by_behavior=exp_hw2_by_behavior,\n        direction_by_group=direction_by_group,\n    )\n\n    exp_hw2_by_behavior = {k: ys for k, ys in exp_hw2_by_behavior.items() if len(ys) > 0}\n    if len(control_hw2) == 0 or len(exp_hw2_by_behavior) == 0:\n        print("  Not enough data to plot.")\n    else:\n        plot_control_vs_exp_behaviors_hw2(\n            control_hw2=control_hw2,\n            exp_hw2_by_behavior=exp_hw2_by_behavior,\n            exp_label_to_color={\n                display_name["challenge_wrong"]: "#238b45",\n                display_name["fix_after_wrong"]: "#74c476",\n                display_name["try_then_ask"]: "#a1d99b",\n                display_name["ask_then_explain"]: "#31a354",\n            },\n            out_pdf=FIG_OUT_PDF,\n            show=SHOW_FIGURES,\n            direction_by_group=direction_by_group,\n        )\n\nif RUN_MATH_PLAGIARISM_EXTRA:\n    def _problem_features_math(\n        seq: List[ChatLabelMath], problem_id: str, attempted_without_chat: bool\n    ) -> Dict[str, Any]:\n        pf = _compute_single_problem_features_math(\n            seq,\n            problem_id=problem_id,\n            attempted_without_chat=attempted_without_chat,\n            nochat_tried_if_attempted=NOCHAT_TRIED_IF_ATTEMPTED,\n            pretry_blank_prop_threshold=PRETRY_BLANK_PROP_THRESHOLD,\n        )\n        # Add math-specific verification signals at problem level so\n        # correction/verification ratio is aligned with behavior definitions.\n        challenge_wrong = any((c.ask_type == "challenge" and c.llm_wrong) for c in seq)\n        fix_after_wrong = False\n        llm_correct: set[str] = set()\n        llm_wrong: set[str] = set()\n        post_correct: set[str] = set()\n        pre_correct: set[str] = set()\n        for c in seq:\n            c_ok, c_bad = _blanks_by_correct(c.ask_blanks)\n            llm_correct.update(c_ok)\n            llm_wrong.update(c_bad)\n            p_ok, _p_bad = _blanks_by_correct(c.post_blanks)\n            post_correct.update(p_ok)\n            pre_ok, _pre_bad = _blanks_by_correct(c.pre_blanks)\n            pre_correct.update(pre_ok)\n        candidate = (llm_wrong - llm_correct) & post_correct & (set(post_correct) - pre_correct)\n        if candidate:\n            fix_after_wrong = True\n        pf["challenge_wrong"] = bool(challenge_wrong)\n        pf["fix_after_wrong"] = bool(fix_after_wrong)\n        return pf\n\n    run_plagiarism_extra_analyses(\n        label="Math",\n        feats=feats,\n        user_problem_chats=user_problem_chats,\n        details=details,\n        target_problems=target_problems,\n        group_name=GROUP,\n        problem_features_fn=_problem_features_math,\n        behaviors_db_path=REPO_ROOT / "data/processed/behaviors/merged_behaviors.db",\n        hw1_entry_stage_name="完成作业 1",\n        output_prefix="a1_math",\n        figures_dir=FIGURES_DIR,\n        show=SHOW_FIGURES,\n        active_trial_threshold=TRIED_THRESHOLD,\n        include_problem_and_cdf_figures=False,\n    )\n\nif OUT_CSV is None:\n    print("\\nOUT_CSV is None; skip writing CSV.")\nelse:\n    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)\n    rows = user_features_to_rows_math(feats)\n    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:\n        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else [])\n        w.writeheader()\n        w.writerows(rows)\n    print("\\nWrote CSV:", OUT_CSV)\n\nif not RUN_STATS:\n    print("\\nRUN_STATS is False; skip stats.")\nelse:\n    try:\n        hw2_by = {c: [f.hw2 for f in rows if f.hw2 is not None] for c, rows in by_cat.items()}\n        run_nonparametric_tests(hw2_by, categories=STATS_CATEGORIES, label="HW2 (raw)")\n    except Exception as e:\n        print("\\nStats failed:", type(e).__name__, str(e))\n\n# LLM accuracy + impact analyses (Math)\nif not RUN_LLM_ACCURACY_IMPACT:\n    print("\\nRUN_LLM_ACCURACY_IMPACT is False; skip LLM accuracy/impact analyses.")\nelse:\n    print("\\n[LLM Accuracy + Wrong-Answer Impact] Start")\n\n    if LLM_ACC_GROUP not in {"All", "Experiment", "Control"}:\n        raise ValueError(f"LLM_ACC_GROUP must be All/Experiment/Control, got {LLM_ACC_GROUP!r}")\n\n    if LLM_ACC_GROUP == "All":\n        analysis_user_ids = [uid for uid in scores.keys() if uid not in excluded_users]\n    else:\n        analysis_user_ids = [\n            uid\n            for uid, s in scores.items()\n            if isinstance(s, dict) and s.get("group") == LLM_ACC_GROUP and uid not in excluded_users\n        ]\n    analysis_user_ids = sorted(set(analysis_user_ids))\n\n    analysis_user_problem_chats: Dict[str, Dict[str, List[ChatLabelMath]]] = {}\n    for uid in analysis_user_ids:\n        chats = iter_labeled_math_chats(\n            labels,\n            uid,\n            stage=STAGE,\n            problem_prefix=PROBLEM_PREFIX,\n            drop_unk_ask=DROP_UNK_ASK,\n        )\n        by_prob: Dict[str, List[ChatLabelMath]] = defaultdict(list)\n        for c in chats:\n            by_prob[c.problem].append(c)\n        analysis_user_problem_chats[uid] = {p: sorted(seq, key=lambda x: x.timestamp) for p, seq in by_prob.items()}\n\n    blank_points = compute_blank_points_map()\n    blank_difficulty = assign_difficulty_thresholds(\n        blank_points,\n        easy_max=0.5,\n        medium_max=1.5,\n    )\n    difficulty_cuts = []\n\n    llm_counts_by_diff: Dict[str, Tuple[int, int]] = defaultdict(lambda: (0, 0))\n    for _uid, pmap in analysis_user_problem_chats.items():\n        for prob, seq in pmap.items():\n            for c in seq:\n                if not isinstance(c.ask_blanks, dict):\n                    continue\n                for blank_id, v in c.ask_blanks.items():\n                    if not isinstance(v, dict):\n                        continue\n                    flag = _parse_correct_flag(v.get("correct"))\n                    if flag is None:\n                        continue\n                    b = blank_difficulty.get((prob, str(blank_id)))\n                    if b is None:\n                        continue\n                    ck, cn = llm_counts_by_diff.get(b, (0, 0))\n                    llm_counts_by_diff[b] = (ck + (1 if flag else 0), cn + 1)\n\n    diff_bins = order_difficulty_bins(sorted(set(blank_difficulty.values()))) if blank_difficulty else []\n    acc_by_diff: Dict[str, Tuple[int, int]] = {b: (0, 0) for b in diff_bins}\n    for b, (k, n) in llm_counts_by_diff.items():\n        ck, cn = acc_by_diff.get(b, (0, 0))\n        acc_by_diff[b] = (ck + k, cn + n)\n\n    print("\\nLLM Accuracy by Difficulty (blank-level):")\n    print("  group =", LLM_ACC_GROUP)\n    if difficulty_cuts:\n        print("  difficulty cut points (blank points):", [f"{c:.3f}" for c in difficulty_cuts])\n    else:\n        print("  difficulty thresholds (blank points): Easy<0.5, Medium<=1.5, Hard>1.5")\n    print("\\t".join(["difficulty", "n_correct", "n_total", "accuracy", "wilson_95%_ci"]))\n    for b in diff_bins:\n        k, n = acc_by_diff.get(b, (0, 0))\n        acc = (k / n) if n else float("nan")\n        lo, hi = wilson_ci(k, n)\n        print("\\t".join([b, str(k), str(n), f"{acc:.3f}", f"[{lo:.3f}, {hi:.3f}]"]))\n\n    plt3 = _maybe_import_matplotlib()\n    if plt3 is None:\n        print("\\nLLM accuracy plot skipped (missing dependency: matplotlib). Install with: `uv add matplotlib`")\n    else:\n        _set_nature_style_v2()\n        import numpy as np  # type: ignore\n\n        fig, ax = plt3.subplots(figsize=(3.6, 3.2))\n        x = np.arange(len(diff_bins))\n        acc_vals = []\n        err_low = []\n        err_high = []\n        n_totals = []\n        for b in diff_bins:\n            k, n = acc_by_diff.get(b, (0, 0))\n            n_totals.append(n)\n            acc = (k / n) if n else 0.0\n            lo, hi = wilson_ci(k, n)\n            acc_vals.append(acc)\n            err_low.append(acc - lo)\n            err_high.append(hi - acc)\n\n        bar_color = "#9ecae1"\n        ax.bar(x, acc_vals, color=bar_color, edgecolor="white", linewidth=0.8, zorder=2)\n        ax.errorbar(x, acc_vals, yerr=[err_low, err_high], fmt="none", ecolor="#2b2b2b", capsize=3, lw=1.0)\n        ax.set_xticks(x)\n        ax.set_xticklabels(diff_bins)\n        ax.set_ylim(0.0, 1.0)\n        _apply_nature_axes(ax, xlabel="Difficulty", ylabel="Accuracy")\n\n        fig.tight_layout()\n        if FIG_LLM_ACC_PDF is not None:\n            FIG_LLM_ACC_PDF.parent.mkdir(parents=True, exist_ok=True)\n            fig.savefig(FIG_LLM_ACC_PDF, dpi=300, bbox_inches="tight")\n            print("Saved:", FIG_LLM_ACC_PDF)\n        if SHOW_FIGURES:\n            plt3.show()\n        plt3.close(fig)\n\n    wrong_outcomes_by_diff: Dict[str, Dict[str, int]] = {}\n    for b in diff_bins:\n        wrong_outcomes_by_diff[b] = {\n            "llm_correct_aligned": 0,\n            "self_corrected": 0,\n            "error_aligned": 0,\n            "total": 0,\n        }\n\n    for _uid, pmap in analysis_user_problem_chats.items():\n        for prob, seq in pmap.items():\n            if not seq:\n                continue\n            ever_wrong: Dict[str, bool] = defaultdict(bool)\n            ever_correct: Dict[str, bool] = defaultdict(bool)\n            for c in seq:\n                if not isinstance(c.ask_blanks, dict):\n                    continue\n                for blank_id, v in c.ask_blanks.items():\n                    if not isinstance(v, dict):\n                        continue\n                    flag = _parse_correct_flag(v.get("correct"))\n                    if flag is None:\n                        continue\n                    if flag:\n                        ever_correct[str(blank_id)] = True\n                    else:\n                        ever_wrong[str(blank_id)] = True\n\n            final_blanks = merge_final_blanks_across_chats(seq)\n\n            for blank_id, was_wrong in ever_wrong.items():\n                if not was_wrong:\n                    continue\n                b = blank_difficulty.get((prob, str(blank_id)))\n                if b is None:\n                    continue\n                v = final_blanks.get(str(blank_id))\n                if not isinstance(v, dict):\n                    continue\n                final_flag = _parse_correct_flag(v.get("correct"))\n                if final_flag is None:\n                    continue\n                wrong_outcomes_by_diff[b]["total"] += 1\n                if final_flag:\n                    if ever_correct.get(str(blank_id), False):\n                        wrong_outcomes_by_diff[b]["llm_correct_aligned"] += 1\n                    else:\n                        wrong_outcomes_by_diff[b]["self_corrected"] += 1\n                else:\n                    wrong_outcomes_by_diff[b]["error_aligned"] += 1\n\n    print("\\nOutcomes After Wrong LLM Answers by Difficulty (blank-level, cross-chat):")\n    print("  Note: \'LLM-Correct Aligned\' means LLM was correct at least once and final blank is correct.")\n    print("        \'Self-Corrected\' means LLM never correct but final blank is correct.")\n    print("        \'Error-Aligned\' means final blank remains incorrect.")\n    print("\\t".join(["difficulty", "n_total", "llm_correct_aligned", "self_corrected", "error_aligned"]))\n    for b in diff_bins:\n        d = wrong_outcomes_by_diff[b]\n        print("\\t".join([b, str(d["total"]), str(d["llm_correct_aligned"]), str(d["self_corrected"]), str(d["error_aligned"])]))\n\n    if plt3 is None:\n        print("\\nWrong-outcome plot skipped (missing dependency: matplotlib). Install with: `uv add matplotlib`")\n    else:\n        _set_nature_style_v2()\n        import numpy as np  # type: ignore\n\n        fig_o, ax_o = plt3.subplots(figsize=(3.6, 3.2))\n        x = np.arange(len(diff_bins))\n        n_totals = []\n        stack_order = ["llm_correct_aligned", "self_corrected"]\n        stack_labels = ["LLM-Consistent Correction", "Self-Correction"]\n        stack_colors = ["#9ECAE1", "#74C476"]\n\n        bottoms = np.zeros(len(diff_bins), dtype=float)\n        for key, lab, col in zip(stack_order, stack_labels, stack_colors):\n            vals = []\n            for i, b in enumerate(diff_bins):\n                d = wrong_outcomes_by_diff[b]\n                n = d["total"]\n                if key == stack_order[0]:\n                    n_totals.append(n)\n                v = (d[key] / n) if n > 0 else 0.0\n                vals.append(v)\n            ax_o.bar(x, vals, bottom=bottoms, color=col, edgecolor="white", linewidth=0.7, label=lab)\n            bottoms += np.array(vals, dtype=float)\n\n        ax_o.set_xticks(x)\n        ax_o.set_xticklabels(diff_bins)\n        ax_o.set_ylim(0.0, 0.7)\n        _apply_nature_axes(ax_o, xlabel="Difficulty", ylabel="Correction ratio")\n        ax_o.legend(frameon=False, loc="upper right", bbox_to_anchor=(1.0, 1.05), fontsize=9)\n\n        fig_o.tight_layout()\n        if FIG_LLM_WRONG_RATE_PDF is not None:\n            FIG_LLM_WRONG_RATE_PDF.parent.mkdir(parents=True, exist_ok=True)\n            fig_o.savefig(FIG_LLM_WRONG_RATE_PDF, dpi=300, bbox_inches="tight")\n            print("Saved:", FIG_LLM_WRONG_RATE_PDF)\n        if SHOW_FIGURES:\n            plt3.show()\n        plt3.close(fig_o)\n\n    correct_not_adopted_by_diff: Dict[str, Dict[str, int]] = {}\n    for b in diff_bins:\n        correct_not_adopted_by_diff[b] = {\n            "misled_by_wrong": 0,\n            "self_wrong": 0,\n            "total_with_llm_correct": 0,\n        }\n\n    for _uid, pmap in analysis_user_problem_chats.items():\n        for prob, seq in pmap.items():\n            if not seq:\n                continue\n            ever_wrong: Dict[str, bool] = defaultdict(bool)\n            ever_correct: Dict[str, bool] = defaultdict(bool)\n            for c in seq:\n                if not isinstance(c.ask_blanks, dict):\n                    continue\n                for blank_id, v in c.ask_blanks.items():\n                    if not isinstance(v, dict):\n                        continue\n                    flag = _parse_correct_flag(v.get("correct"))\n                    if flag is None:\n                        continue\n                    if flag:\n                        ever_correct[str(blank_id)] = True\n                    else:\n                        ever_wrong[str(blank_id)] = True\n\n            final_blanks = merge_final_blanks_across_chats(seq)\n\n            for blank_id, was_correct in ever_correct.items():\n                if not was_correct:\n                    continue\n                b = blank_difficulty.get((prob, str(blank_id)))\n                if b is None:\n                    continue\n                v = final_blanks.get(str(blank_id))\n                if not isinstance(v, dict):\n                    continue\n                final_flag = _parse_correct_flag(v.get("correct"))\n                if final_flag is None:\n                    continue\n                d = correct_not_adopted_by_diff[b]\n                d["total_with_llm_correct"] += 1\n                if not final_flag:\n                    if ever_wrong.get(str(blank_id), False):\n                        d["misled_by_wrong"] += 1\n                    else:\n                        d["self_wrong"] += 1\n\n    print("\\nNon-adoption After LLM Correct Answers by Difficulty (blank-level, cross-chat):")\n    print("  Note: \'Misled by Wrong\' means LLM was wrong at least once and final blank is incorrect.")\n    print("        \'Self Wrong\' means LLM always correct but final blank is incorrect.")\n    print("\\t".join(["difficulty", "n_total", "misled_by_wrong", "self_wrong", "not_adopted_rate"]))\n    for b in diff_bins:\n        d = correct_not_adopted_by_diff[b]\n        total = d["total_with_llm_correct"]\n        not_adopted = d["misled_by_wrong"] + d["self_wrong"]\n        rate = (not_adopted / total) if total > 0 else float("nan")\n        print(\n            "\\t".join(\n                [b, str(total), str(d["misled_by_wrong"]), str(d["self_wrong"]), f"{rate:.3f}"]\n            )\n        )\n\n    if plt3 is None:\n        print(\n            "\\nCorrect-not-adopted plot skipped (missing dependency: matplotlib). Install with: `uv add matplotlib`"\n        )\n    else:\n        _set_nature_style_v2()\n        import numpy as np  # type: ignore\n\n        fig_c, ax_c = plt3.subplots(figsize=(3.6, 3.2))\n        x = np.arange(len(diff_bins))\n        stack_order = ["misled_by_wrong", "self_wrong"]\n        stack_labels = ["LLM-Error-Influenced Non-Adoption", "Self-Origin Non-Adoption"]\n        stack_colors = ["#FC9272", "#9ECAE1"]\n\n        bottoms = np.zeros(len(diff_bins), dtype=float)\n        for key, lab, col in zip(stack_order, stack_labels, stack_colors):\n            vals = []\n            for b in diff_bins:\n                d = correct_not_adopted_by_diff[b]\n                n = d["total_with_llm_correct"]\n                v = (d[key] / n) if n > 0 else 0.0\n                vals.append(v)\n            ax_c.bar(x, vals, bottom=bottoms, color=col, edgecolor="white", linewidth=0.7, label=lab)\n            bottoms += np.array(vals, dtype=float)\n\n        ax_c.set_xticks(x)\n        ax_c.set_xticklabels(diff_bins)\n        ax_c.set_ylim(0.0, 0.7)\n        _apply_nature_axes(ax_c, xlabel="Difficulty", ylabel="Non-adoption ratio")\n        ax_c.legend(frameon=False, loc="upper right", bbox_to_anchor=(1.0, 1.05), fontsize=9)\n\n        fig_c.tight_layout()\n        if FIG_LLM_CORRECT_NOT_ADOPTED_PDF is not None:\n            FIG_LLM_CORRECT_NOT_ADOPTED_PDF.parent.mkdir(parents=True, exist_ok=True)\n            fig_c.savefig(FIG_LLM_CORRECT_NOT_ADOPTED_PDF, dpi=300, bbox_inches="tight")\n            print("Saved:", FIG_LLM_CORRECT_NOT_ADOPTED_PDF)\n        if SHOW_FIGURES:\n            plt3.show()\n        plt3.close(fig_c)\n\n# %%\n'

def _set_output_dir(figures_dir: Optional[Path] = None, *, show_figures: bool = False) -> Path:
    global FIGURES_DIR, SHOW_FIGURES
    FIGURES_DIR = Path(figures_dir) if figures_dir is not None else REPO_ROOT / "figures"
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    SHOW_FIGURES = bool(show_figures)
    return FIGURES_DIR


def _privacy_safe_run_source(source: str) -> str:
    """Keep generated script-mode notebook output free of local absolute paths."""
    replacements = {
        'print("Loading:", SCORES_PATH)': 'print("Loading:", relative_path(SCORES_PATH, base=REPO_ROOT))',
        'print("Loading:", DETAILS_PATH)': 'print("Loading:", relative_path(DETAILS_PATH, base=REPO_ROOT))',
        'print("Loading:", EXCLUDE_USERS_PATH)': 'print("Loading:", relative_path(EXCLUDE_USERS_PATH, base=REPO_ROOT))',
        'print("Loading:", MATH_SCORES_PATH)': 'print("Loading:", relative_path(MATH_SCORES_PATH, base=REPO_ROOT))',
        'print("Loading:", VALID_USERS_PATH)': 'print("Loading:", relative_path(VALID_USERS_PATH, base=REPO_ROOT))',
    }
    for old, new in replacements.items():
        source = source.replace(old, new)
    return source


def run_python_behavior_analysis(*, figures_dir: Optional[Path] = None, show_figures: bool = False) -> dict[str, Any]:
    """Generate the Python behavior-outcome panel used by the main paper."""
    global LABELS_PATH, SCORES_PATH, DETAILS_PATH, EXCLUDE_USERS_PATH
    global GROUP, STAGE, PROBLEM_PREFIX, DROP_UNK_ASK, APPLY_EXCLUDE_USERS
    global PROBLEM_DENOM_POLICY, NOCHAT_TRIED_IF_ATTEMPTED, TARGET_PROBLEMS
    global TRIED_THRESHOLD, COPY_FIRST_THRESHOLD, PRECEDENCE
    global OUT_CSV, RUN_STATS, STATS_CATEGORIES, PLOT_CONTROL_VS_EXP, FIG_OUT_PDF
    global PLOT_SHOW_N_IN_XTICK, RUN_PY_PLAGIARISM_EXTRA, SAVE_SINGLE_BEHAVIOR_HETEROGENEITY
    global RUN_PY_LLM_ACCURACY, PY_LLM_ACC_GROUP, FIG_PY_LLM_ACC_PDF

    fig_dir = _set_output_dir(figures_dir, show_figures=show_figures)
    LABELS_PATH = _data_path("data/annotation/a1_chat_labels.json")
    SCORES_PATH = REPO_ROOT / "data/annotation/python_scores.json"
    DETAILS_PATH = REPO_ROOT / "data/annotation/python_details.json"
    EXCLUDE_USERS_PATH = REPO_ROOT / "data/processed/exclude_user.csv"
    GROUP = "Experiment"
    STAGE = "a1"
    PROBLEM_PREFIX = "py_"
    DROP_UNK_ASK = True
    APPLY_EXCLUDE_USERS = True
    PROBLEM_DENOM_POLICY = "attempted_or_chatted"
    NOCHAT_TRIED_IF_ATTEMPTED = True
    TARGET_PROBLEMS = None
    TRIED_THRESHOLD = 0.25
    COPY_FIRST_THRESHOLD = 0.75
    PRECEDENCE = PYTHON_A1_PRECEDENCE
    OUT_CSV = None
    RUN_STATS = True
    STATS_CATEGORIES = ("no_chat", "mindless_copy", "try_then_ask", "ask_then_explain")
    PLOT_CONTROL_VS_EXP = True
    FIG_OUT_PDF = fig_dir / "a1_hw2_control_vs_exp_behavior.pdf"
    PLOT_SHOW_N_IN_XTICK = True
    RUN_PY_PLAGIARISM_EXTRA = False
    SAVE_SINGLE_BEHAVIOR_HETEROGENEITY = False
    RUN_PY_LLM_ACCURACY = False
    PY_LLM_ACC_GROUP = "All"
    FIG_PY_LLM_ACC_PDF = fig_dir / "a1_py_llm_accuracy_by_difficulty.pdf"
    exec(_privacy_safe_run_source(_PYTHON_BEHAVIOR_RUN_SOURCE), globals(), globals())
    return {"output_files": [FIG_OUT_PDF]}


def run_game_theory_behavior_analysis(*, figures_dir: Optional[Path] = None, show_figures: bool = False) -> dict[str, Any]:
    """Generate the Game Theory behavior-outcome and twin heterogeneity panels."""
    global LABELS_PATH, MATH_SCORES_PATH, VALID_USERS_PATH, EXCLUDE_USERS_PATH
    global GROUP, STAGE, PROBLEM_PREFIX, DROP_UNK_ASK, APPLY_EXCLUDE_USERS
    global PROBLEM_DENOM_POLICY, NOCHAT_TRIED_IF_ATTEMPTED, TARGET_PROBLEMS
    global TRIED_THRESHOLD, COPY_FIRST_THRESHOLD, PRETRY_BLANK_PROP_THRESHOLD, PRECEDENCE
    global OUT_CSV, RUN_STATS, STATS_CATEGORIES, PLOT_CONTROL_VS_EXP, FIG_OUT_PDF
    global PLOT_SHOW_N_IN_XTICK, RUN_MATH_PLAGIARISM_EXTRA, RUN_LLM_ACCURACY_IMPACT
    global LLM_ACC_GROUP, LLM_DIFFICULTY_BINS, FIG_LLM_ACC_PDF, FIG_LLM_WRONG_RATE_PDF
    global FIG_LLM_CORRECT_NOT_ADOPTED_PDF

    fig_dir = _set_output_dir(figures_dir, show_figures=show_figures)
    LABELS_PATH = _data_path("data/annotation/a1_chat_labels.json")
    MATH_SCORES_PATH = _data_path("data/llm/math_score_reviews_with_answers.json", "data/annotation/math_score_reviews_with_answers.json")
    VALID_USERS_PATH = REPO_ROOT / "data/processed/validuser_merged.csv"
    EXCLUDE_USERS_PATH = REPO_ROOT / "data/processed/exclude_user.csv"
    GROUP = "Experiment"
    STAGE = "a1"
    PROBLEM_PREFIX = "math_"
    DROP_UNK_ASK = True
    APPLY_EXCLUDE_USERS = True
    PROBLEM_DENOM_POLICY = "attempted_or_chatted"
    NOCHAT_TRIED_IF_ATTEMPTED = True
    TARGET_PROBLEMS = None
    TRIED_THRESHOLD = 0.5
    COPY_FIRST_THRESHOLD = 0.5
    PRETRY_BLANK_PROP_THRESHOLD = 0.8
    PRECEDENCE = MATH_A1_PRECEDENCE
    OUT_CSV = None
    RUN_STATS = True
    STATS_CATEGORIES = ("no_chat", "mindless_copy", "challenge_wrong", "fix_after_wrong", "try_then_ask", "ask_then_explain")
    PLOT_CONTROL_VS_EXP = True
    FIG_OUT_PDF = fig_dir / "a1_math_hw2_control_vs_exp_behavior.pdf"
    PLOT_SHOW_N_IN_XTICK = True
    RUN_MATH_PLAGIARISM_EXTRA = False
    RUN_LLM_ACCURACY_IMPACT = False
    LLM_ACC_GROUP = "All"
    LLM_DIFFICULTY_BINS = 3
    FIG_LLM_ACC_PDF = fig_dir / "a1_math_llm_accuracy_by_difficulty.pdf"
    FIG_LLM_WRONG_RATE_PDF = fig_dir / "a1_math_llm_wrong_outcome_by_difficulty.pdf"
    FIG_LLM_CORRECT_NOT_ADOPTED_PDF = fig_dir / "a1_math_llm_correct_not_adopted_by_difficulty.pdf"
    exec(_privacy_safe_run_source(_MATH_BEHAVIOR_RUN_SOURCE), globals(), globals())
    return {"output_files": [FIG_OUT_PDF, fig_dir / "a1_behavior_heterogeneity_twin_python_game_theory.pdf"]}
