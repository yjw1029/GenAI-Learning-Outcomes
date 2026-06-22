"""Helper functions for the reviewer-facing participant feedback notebook."""
"""
Feedback analysis plots (block-executable).

Block 1: Load and prepare post-survey data
Block 2: Map Likert and multi-select values
Block 3: Plotting helpers
Block 4: Generate figures
"""
import json
import math
import sys
import textwrap
from pathlib import Path
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import colors as mcolors
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from dataclasses import dataclass

from analyze.utils.display import relative_path
import analyze.behavior.a1 as behavior_a1
from analyze.behavior.category_rules import (
    MATH_A1_PRECEDENCE,
    PYTHON_A1_PRECEDENCE,
    pick_math_a1_category,
    pick_python_a1_category,
)

# Add project root to path. Jupyter does not define __file__, so locate the
# repository from the current working directory when running as a notebook.
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


from analyze.config import POSTSURVEY_FILE, PRESURVEY_FILE, VALIDUSER_FILE
from analyze.config.encoding import FUTURE_GPT_WILLINGNESS_MAP
from analyze.config.scoring import MATH_SCORE_MAP
from analyze.core import load_valid_users

# Global figure display toggle (set False for headless/script runs).
SHOW_FIGURES = True

# Override figure output directory for this script only.
FIGURES_DIR = REPO_ROOT / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# =========================
# Functions
# =========================
def set_nature_style() -> None:
    plt.rcParams.update(
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


LABEL_TRIED_Y = "y"
LABEL_TRIED_N = "n"
VERBATIM_MODES = {"copy", "type"}
COPYLIKE_MODES = {"copy", "type", "mix"}
EXPLAIN_GOALS = {"explain"}
EXPLAIN_TYPES = {"concept"}
FINAL_ANSWER_GOALS = {"final_answer"}
FINAL_ANSWER_TYPES = {"answer"}

TRIED_THRESHOLD = 0.25
COPY_FIRST_THRESHOLD = 0.75
PRECEDENCE = PYTHON_A1_PRECEDENCE

MATH_TRIED_THRESHOLD = 0.5
MATH_COPY_FIRST_THRESHOLD = 0.5
MATH_PRETRY_BLANK_PROP_THRESHOLD = 0.8
MATH_PRECEDENCE = MATH_A1_PRECEDENCE
MATH_VERBATIM_MODES = VERBATIM_MODES

PROACTIVE_CRITIC_COLOR = "#31a354"
PASSIVE_COLOR = "#7f7f7f"
CONTROL_COLOR = "#c6dbef"
EXP_COLOR = "#a1d99b"

PRE_WILLINGNESS_KEY = "大语言对话模型的使用_8"
PRE_RISK_KEY = "大语言对话模型的使用_6"
POST_WILLINGNESS_KEY = "观点｜未来_1"
POST_RISK_KEY = "观点｜未来_2"

POST_WILLINGNESS_MAP = {
    "未来非常愿意使用": 4,
    "未来比较愿意使用": 3,
    "中立/不确定": 2,
    "未来不太愿意使用": 1,
    "未来完全不愿意使用": 0,
    "其他": math.nan,
}

RISK_OVERLAP_ITEMS = [
    "我担心过度依赖这类工具，它可能会削弱我的批判性思维和解决问题能力。",
    "我担心这些工具提供的信息可能不够准确或可靠。",
    "我担心这会减少我与同学/老师之间的人际交流和合作机会。",
]
RISK_LABELS = {
    "我担心过度依赖这类工具，它可能会削弱我的批判性思维和解决问题能力。": "Overreliance",
    "我担心这些工具提供的信息可能不够准确或可靠。": "Inaccuracy",
    "我担心这会减少我与同学/老师之间的人际交流和合作机会。": "Less\nInteraction",
}


def _darken_color(color: str, factor: float = 0.8) -> str:
    rgb = np.array(mcolors.to_rgb(color))
    darker = np.clip(rgb * factor, 0, 1)
    return mcolors.to_hex(darker)


def _normalize_multiselect(value: object) -> set[str] | None:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, list):
        return {str(v).strip() for v in value if str(v).strip()}
    if isinstance(value, str):
        val = value.strip()
        if not val:
            return set()
        if ";" in val:
            return {v.strip() for v in val.split(";") if v.strip()}
        return {val}
    return {str(value).strip()}


def _map_post_willingness(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, str):
        val = value.strip()
        if not val:
            return None
        mapped = POST_WILLINGNESS_MAP.get(val)
        if mapped is None:
            return None
        if isinstance(mapped, float) and math.isnan(mapped):
            return None
        return float(mapped)
    return None


def _map_pre_willingness(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, str):
        val = value.strip()
        if not val:
            return None
        mapped = FUTURE_GPT_WILLINGNESS_MAP.get(val)
        if mapped is None:
            return None
        return float(mapped)
    return None
def load_postsurvey_data() -> pd.DataFrame:
    """Load and process post-survey data."""
    print("=" * 60)
    print("Loading Post-Survey Data")
    print("=" * 60)

    with open(POSTSURVEY_FILE, "r", encoding="utf-8") as f:
        postsurvey = json.load(f)

    print(f"Loaded post-survey for {len(postsurvey)} users")

    data = []
    for username, survey in postsurvey.items():
        row = {"username": username}
        row.update(survey)
        data.append(row)

    df = pd.DataFrame(data)

    python_df, math_df = load_valid_users(VALIDUSER_FILE)

    valid_users_df = pd.concat(
        [
            python_df[python_df["group"] == 1],
            math_df[math_df["group"] == 1],
        ],
        ignore_index=True,
    )

    print(f"Loaded {len(valid_users_df)} valid experiment users from {relative_path(VALIDUSER_FILE)}")

    df = df.merge(valid_users_df[["username", "group", "course"]], on="username", how="inner")

    print(f"Filtered to {len(df)} experiment group users with post-survey data")

    return df


def load_prepost_attitudes() -> pd.DataFrame:
    print("\n" + "=" * 60)
    print("Loading Pre/Post Attitudes Data")
    print("=" * 60)

    with open(PRESURVEY_FILE, "r", encoding="utf-8") as f:
        presurvey = json.load(f)
    with open(POSTSURVEY_FILE, "r", encoding="utf-8") as f:
        postsurvey = json.load(f)

    python_df, math_df = load_valid_users(VALIDUSER_FILE)
    valid_users_df = pd.concat([python_df, math_df], ignore_index=True)

    rows = []
    for _, row in valid_users_df.iterrows():
        username = row["username"]
        pre = presurvey.get(username, {})
        post = postsurvey.get(username, {})
        rows.append(
            {
                "username": username,
                "group": int(row["group"]),
                "course": row["course"],
                "pre_willingness": _map_pre_willingness(pre.get(PRE_WILLINGNESS_KEY)),
                "post_willingness": _map_post_willingness(post.get(POST_WILLINGNESS_KEY)),
                "pre_risks": _normalize_multiselect(pre.get(PRE_RISK_KEY)),
                "post_risks": _normalize_multiselect(post.get(POST_RISK_KEY)),
            }
        )

    df = pd.DataFrame(rows)
    print(f"Loaded pre/post attitude data for {len(df)} valid users")
    return df


def map_likert_scale_values(df: pd.DataFrame) -> pd.DataFrame:
    """Map Likert scale responses to numeric values."""
    print("\nMapping Likert scale values...")

    value_maps = {
        "人工判断性能_0": {
            "非常准确": 5,
            "相对准确": 4,
            "一般": 3,
            "相对不准确": 2,
            "非常不准确": 1,
            "我无法使用对话助手": 0,
        },
        "人工判断性能_1": {
            "非常准确": 5,
            "相对准确": 4,
            "一般": 3,
            "相对不准确": 2,
            "非常不准确": 1,
            "我无法使用对话助手": 0,
        },
        "人工判断性能_2": {
            "总是能够调整": 5,
            "经常能够调整": 4,
            "有时能够调整": 3,
            "很少能够调整": 2,
            "从未能够调整": 1,
            "我无法使用对话助手": 0,
        },
        "人工判断性能_3": {
            "总是能考虑到我的学习进度": 5,
            "经常能考虑到我的学习进度": 4,
            "有时能考虑到我的学习进度": 3,
            "很少能考虑到我的学习进度": 2,
            "从不能考虑到我的学习进度": 1,
            "我无法使用对话助手": 0,
        },
        "人工判断性能_4": {
            "显著提高": 5,
            "稍微提高": 4,
            "没有变化": 3,
            "稍微减少": 2,
            "显著减少": 1,
            "我无法使用对话助手": 0,
        },
        "人工判断性能_5": {
            "显著提高": 5,
            "稍微提高": 4,
            "没有变化": 3,
            "稍微减少": 2,
            "显著减少": 1,
            "我无法使用对话助手": 0,
        },
        "人工判断性能_6": {
            "显著提高": 5,
            "稍微提高": 4,
            "没有变化": 3,
            "稍微减少": 2,
            "显著减少": 1,
            "我无法使用对话助手": 0,
        },
        "人工判断性能_7": {
            "显著提高": 5,
            "稍微提高": 4,
            "没有变化": 3,
            "稍微减少": 2,
            "显著减少": 1,
            "我无法使用对话助手": 0,
        },
        "人工判断性能_8": {
            "过于礼貌，有时显得不必要": 2,
            "礼貌程度适中，恰到好处": 5,
            "无法评价/不清楚": 3,
            "不够礼貌，需要更加客气": 4,
            "非常不礼貌": 1,
            "我无法使用对话助手": 0,
        },
        "人工判断性能_9": {
            "过于耐心，有时显得不必要": 2,
            "耐心程度适中，恰到好处": 5,
            "无法评价/不清楚": 3,
            "不够耐心，需要更加客气": 4,
            "非常不耐心": 1,
            "我无法使用对话助手": 0,
        },
        "人工判断性能_10": {
            "显著更有趣": 5,
            "稍微更有趣": 4,
            "大致相同": 3,
            "稍微更无聊": 2,
            "显著更无聊": 1,
            "我无法使用对话助手": 0,
        },
        "人工判断性能_11": {
            "非常受鼓励": 5,
            "比较受鼓励": 4,
            "一般": 3,
            "不太受鼓励": 2,
            "完全不受鼓励": 1,
            "我无法使用对话助手": 0,
        },
    }

    for col, mapping in value_maps.items():
        if col in df.columns:
            df[col] = df[col].map(mapping)

    friendly_names = {
        "人工判断性能_0": "Response accuracy",
        "人工判断性能_1": "Question comprehension",
        "人工判断性能_2": "Response personalization",
        "人工判断性能_3": "Learning progress awareness",
        "人工判断性能_4": "Course learning effectiveness",
        "人工判断性能_5": "Assignment effectiveness",
        "人工判断性能_6": "Review effectiveness",
        "人工判断性能_7": "Exam effectiveness",
        "人工判断性能_8": "Politeness",
        "人工判断性能_9": "Patience",
        "人工判断性能_10": "Enjoyability",
        "人工判断性能_11": "Exploration encouragement",
    }

    return df.rename(columns=friendly_names)


def map_multiselect_values(df: pd.DataFrame) -> pd.DataFrame:
    """Map Chinese multi-select values to English."""
    print("\nMapping multi-select values to English...")

    value_maps = {
        "目的_1": {
            "帮助总结参考材料": "Summarize sources",
            "进行相关知识的概念解释": "Concept explanations",
            "得到具体问题的答案": "Specific answers",
            "得到具体问题答案的解释": "Answer explanations",
            "得到知识点的解题思路": "Solution approach",
            "帮助进行题目推荐（若适用）": "Problem suggestions",
            "帮助检验答案的正确性": "Answer checking",
            "获得对已有题目自己改编问题的答案": "Variant questions",
            "我无法使用对话助手": "Unable to use assistant",
            "Other": "Other",
        },
        "目的_3": {
            "我首先独立尝试完成任务，遇到困难时才使用GPT/GPTMentor进行辅助": "Use when stuck",
            "我首先独立尝试完成任务，遇到困难时才使用对话助手进行辅助": "Use when stuck",
            "我在整个学习过程中都结合使用GPT/GPTMentor，从开始到结束": "Throughout learning",
            "我在整个学习过程中都结合使用对话助手，从开始到结束": "Throughout learning",
            "我主要在学习的初始阶段使用GPT/GPTMentor来获得一个大致的理解，之后独立深入学习": "Early-stage only",
            "我主要在学习的初始阶段使用对话助手来获得一个大致的理解，之后独立深入学习": "Early-stage only",
            "我在学习过程的后期使用GPT/GPTMentor进行复习和巩固已学内容": "Late-stage review",
            "我在学习过程的后期使用对话助手进行复习和巩固已学内容": "Late-stage review",
            "我不使用或很少使用GPT/GPTMentor进行学习": "Rarely use",
            "我不使用或很少使用对话助手进行学习": "Rarely use",
            "我无法使用对话助手": "Unable to use assistant",
            "Other": "Other",
        },
        "目的_2": {
            "帮助总结参考材料": "Summarize sources",
            "进行相关知识的概念解释": "Concept explanations",
            "得到题目的答案": "Problem answers",
            "得到题目答案的解释": "Answer explanations",
            "得到知识点的解题思路": "Solution approach",
            "验证我提供的答案": "Answer checking",
            "没有帮助": "No help",
            "我无法使用对话助手": "Unable to use assistant",
            "Other": "Other",
        },
    }

    def map_value(value: object, mapping_dict: dict[str, str]) -> object:
        if isinstance(value, list):
            mapped = []
            for v in value:
                v_str = str(v).strip()
                if not v_str:
                    continue
                if v_str.startswith("其他："):
                    mapped.append("Other")
                else:
                    mapped.append(mapping_dict.get(v_str, v_str))
            return mapped

        try:
            if pd.isna(value):
                return value
        except (ValueError, TypeError):
            pass

        if not isinstance(value, str):
            return mapping_dict.get(value, value)

        value = value.strip()
        if not value:
            return value
        if value.startswith("其他："):
            return "Other"

        if ";" in value:
            items = [item.strip() for item in value.split(";") if item.strip()]
            mapped_items = []
            for item in items:
                if item.startswith("其他："):
                    mapped_items.append("Other")
                else:
                    mapped_items.append(mapping_dict.get(item, item))
            return ";".join(mapped_items)

        return mapping_dict.get(value, value)

    for col, mapping in value_maps.items():
        if col in df.columns:
            df[col] = df[col].apply(lambda x: map_value(x, mapping))

    return df


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
    pretry_rate = _pretry_rate_for_problem(problem_id, seq)
    any_answer_request = any(
        ((c.ask_type in FINAL_ANSWER_TYPES) or (c.ask_goal in FINAL_ANSWER_GOALS)) for c in seq
    )
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


def _compute_behavior_supergroup(
    series: pd.Series,
    *,
    proactive_critic_categories: set[str],
    passive_categories: set[str],
) -> pd.Series:
    def _map(cat: object) -> str:
        if cat in proactive_critic_categories:
            return "proactive_critic"
        if cat in passive_categories:
            return "passive"
        return "passive"

    return series.map(_map)


def add_behavior_supergroup_python(python_df: pd.DataFrame) -> pd.DataFrame:
    labels_path = REPO_ROOT / "data/annotation/a1_chat_labels.json"
    python_details_path = REPO_ROOT / "data/annotation/python_details.json"

    df = python_df.copy()
    df["behavior_supergroup"] = pd.NA
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

    proactive_critic_categories = {"try_then_ask", "ask_then_explain"}
    passive_categories = {"mindless_copy", "no_chat"}
    df_exp["behavior_supergroup"] = _compute_behavior_supergroup(
        df_exp["a1_behavior_group"],
        proactive_critic_categories=proactive_critic_categories,
        passive_categories=passive_categories,
    )
    df.loc[df_exp.index, "behavior_supergroup"] = df_exp["behavior_supergroup"]
    return df


def add_behavior_supergroup_math(math_df: pd.DataFrame) -> pd.DataFrame:
    labels_path = REPO_ROOT / "data/annotation/a1_chat_labels.json"
    math_details_path = REPO_ROOT / "data/annotation/math_score_reviews_with_answers.json"

    df = math_df.copy()
    df["behavior_supergroup"] = pd.NA
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

    proactive_critic_categories = {"try_then_ask", "ask_then_explain", "fix_after_wrong", "challenge_wrong"}
    passive_categories = {"mindless_copy", "no_chat"}
    df_exp["behavior_supergroup"] = _compute_behavior_supergroup(
        df_exp["a1_behavior_group"],
        proactive_critic_categories=proactive_critic_categories,
        passive_categories=passive_categories,
    )
    df.loc[df_exp.index, "behavior_supergroup"] = df_exp["behavior_supergroup"]
    return df


def _save_and_maybe_show(fig: plt.Figure, output_path: Path) -> None:
    fig.savefig(output_path, bbox_inches="tight")
    print(f"Saved plot to: {relative_path(output_path)}")
    if SHOW_FIGURES:
        plt.show()
    plt.close(fig)


def plot_survey_ratings(
    dataframe: pd.DataFrame,
    columns_to_plot: list[str],
    rating_labels: dict[int, str] | None = None,
    include_zero_rating: bool = False,
    figure_size: tuple[int, int] = (10, 6),
    colors: list[str] | None = None,
    fontsize: int = 10,
    y_label_width: int = 15,
    bbox_to_anchor: tuple[float, float] = (0.5, 1.25),
    ncol: int = 3,
) -> plt.Axes:
    """Plot survey ratings as stacked horizontal bar chart."""
    import numpy as np

    df_copy = dataframe[columns_to_plot].copy()

    if colors is None:
        colors = ["#d73027", "#fc8d59", "#fee090", "#91bfdb", "#4575b4"]
        if include_zero_rating:
            colors = ["#999999"] + colors

    friendly_labels = {}
    for col in columns_to_plot:
        wrapped_label = "\n".join(textwrap.wrap(col.replace("_", " "), width=y_label_width))
        friendly_labels[col] = wrapped_label

    percentages = pd.DataFrame()
    rating_labels = rating_labels or {}

    for col in columns_to_plot:
        if col in df_copy.columns:
            if not include_zero_rating:
                data = df_copy[df_copy[col] > 0][col]
            else:
                data = df_copy[col]
            value_counts = data.value_counts(normalize=True).sort_index() * 100
            percentages[col] = value_counts.reindex(rating_labels.keys()).fillna(0)

    order = [0, 1, 2, 3, 4, 5] if include_zero_rating else [1, 2, 3, 4, 5]
    percentages = percentages.reindex(order)
    percentages.columns = [friendly_labels.get(col, col) for col in percentages.columns]

    fig = plt.figure(figsize=figure_size)
    ax = percentages.T.plot(kind="barh", stacked=True, figsize=figure_size, color=colors)

    plt.xlabel("Percentage (%)", fontsize=fontsize)
    plt.ylabel("", fontsize=fontsize)

    ax.tick_params(axis="both", labelsize=fontsize)
    plt.subplots_adjust(left=0.2)

    actual_ratings = sorted(
        list(set(np.concatenate([df_copy[col].dropna().unique() for col in columns_to_plot])))
    )
    if not include_zero_rating:
        actual_ratings = [r for r in actual_ratings if r > 0]

    handles, labels = ax.get_legend_handles_labels()
    if include_zero_rating:
        new_labels = [rating_labels.get(i, f"Rating {i}") for i in range(len(handles))]
    else:
        new_labels = [rating_labels.get(i + 1, f"Rating {i + 1}") for i in range(len(handles))]

    ax.get_legend().remove()
    plt.legend(
        handles,
        new_labels,
        title="",
        title_fontsize=fontsize,
        fontsize=fontsize,
        loc="upper center",
        bbox_to_anchor=bbox_to_anchor,
        ncol=ncol,
    )

    plt.xlim(0, 100)
    plt.axvline(x=50, color="gray", linestyle="--", alpha=0.5)
    plt.grid(False)
    plt.tight_layout()

    return ax


def plot_multi_select_pie(
    dataframe: pd.DataFrame, column: str, fontsize: int = 26
) -> tuple[plt.Figure, plt.Axes]:
    """Plot multi-select question as pie chart."""
    print(f"\nGenerating pie chart for: {column}")

    excluded_values = {
        "Unable to use assistant",
        "Unable to access assistant",
        "Inaccessible",
        "No assistance provided",
    }

    category_counts: dict[str, int] = {}
    total_responses = 0

    for response in dataframe[column].dropna():
        total_responses += 1
        if isinstance(response, list):
            for val in response:
                val = str(val).strip()
                if val not in excluded_values:
                    category_counts[val] = category_counts.get(val, 0) + 1
        elif isinstance(response, str) and ";" in response:
            for val in response.split(";"):
                val = val.strip()
                if val not in excluded_values:
                    category_counts[val] = category_counts.get(val, 0) + 1
        else:
            val = str(response).strip()
            if val not in excluded_values:
                category_counts[val] = category_counts.get(val, 0) + 1

    if total_responses > 0:
        for cat in category_counts:
            category_counts[cat] = (category_counts[cat] / total_responses) * 100

    sorted_counts = dict(sorted(category_counts.items(), key=lambda x: x[1], reverse=True))

    fig, ax = plt.subplots(figsize=(9.6, 7.3), dpi=300)
    colors = sns.color_palette("viridis", len(sorted_counts))

    wedges, texts, autotexts = ax.pie(
        sorted_counts.values(),
        labels=None,
        autopct=lambda pct: f"{pct:.1f}%" if pct > 5 else "",
        colors=colors,
        startangle=90,
        pctdistance=0.75,
        wedgeprops={"edgecolor": "white", "linewidth": 1.5},
        textprops={"fontsize": fontsize, "color": "white", "fontweight": "bold"},
    )

    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")

    centre_circle = plt.Circle((0, 0), 0.5, fc="white", edgecolor="white")
    ax.add_patch(centre_circle)

    ax.legend(
        wedges,
        [f"{label}" for label in sorted_counts.keys()],
        loc="center left",
        bbox_to_anchor=(0.9, 0.47),
        fontsize=fontsize - 1,
        frameon=False,
        handlelength=1,
        handleheight=1,
        ncol=1,
    )

    plt.tight_layout()

    return fig, ax


# =========================
# Likert point + 95% CI plot
# =========================
def _mean_ci_bounds(series: pd.Series) -> tuple[float, float, float]:
    series = series.dropna()
    n = series.shape[0]
    if n < 2:
        return series.mean(), 0.0, 0.0
    mean = series.mean()
    sd = series.std(ddof=1)
    se = sd / (n ** 0.5)
    ci95 = 1.96 * se
    ci90 = 1.645 * se
    return mean, ci90, ci95


def plot_likert_point_ci_by_course(
    dataframe: pd.DataFrame,
    items: list[str],
    title: str,
    course_colors: dict[str, str],
) -> tuple[plt.Figure, plt.Axes]:
    records = []
    for course in ["python", "math"]:
        course_df = dataframe[dataframe["course"] == course]
        for item in items:
            if item not in course_df.columns:
                continue
            series = course_df[item]
            series = series[series > 0].dropna()
            if series.empty:
                continue
            mean, ci90, ci95 = _mean_ci_bounds(series)
            records.append(
                {
                    "course": course,
                    "item": item,
                    "mean": mean,
                    "ci90": ci90,
                    "ci95": ci95,
                    "n": series.shape[0],
                }
            )

    if not records:
        raise ValueError(f"No valid Likert data for: {title}")

    plot_df = pd.DataFrame(records)
    manual_labels = {
        "Response accuracy": "Response\nAccuracy",
        "Question comprehension": "Question\nComprehension",
        "Response personalization": "Response\nPersonalization",
        "Learning progress awareness": "Learning Progress\nAwareness",
        "Course learning effectiveness": "Course Learning\nEffectiveness",
        "Assignment effectiveness": "Assignment\nEffectiveness",
        "Review effectiveness": "Review\nEffectiveness",
        "Exam effectiveness": "Exam\nEffectiveness",
        "Politeness": "Politeness",
        "Patience": "Patience",
        "Enjoyability": "Enjoyability",
        "Exploration encouragement": "Exploration\nEncouragement",
    }
    plot_df["item_wrapped"] = plot_df["item"].apply(lambda s: manual_labels.get(s, s))

    fig, ax = plt.subplots(figsize=(6.1, 7.0), dpi=300)

    item_order = list(dict.fromkeys(plot_df["item"].tolist()))
    y_base = {item: idx for idx, item in enumerate(item_order)}
    offset = 0.15

    for course in ["math", "python"]:
        color = course_colors[course]
        sub = plot_df[plot_df["course"] == course]
        y_positions = [
            y_base[item] - offset if course == "math" else y_base[item] + offset
            for item in sub["item"]
        ]
        ax.errorbar(
            sub["mean"],
            y_positions,
            xerr=sub["ci95"],
            fmt="none",
            ecolor=color,
            elinewidth=1.2,
            capsize=4,
            alpha=0.9,
        )
        ax.errorbar(
            sub["mean"],
            y_positions,
            xerr=sub["ci90"],
            fmt="o",
            color=color,
            ecolor=color,
            elinewidth=2.6,
            capsize=0,
            markersize=7,
            markeredgecolor="white",
            markeredgewidth=0.8,
        )

    ax.set_yticks([y_base[item] for item in item_order])
    ax.set_yticklabels([manual_labels.get(item, item) for item in item_order])
    ax.set_xlim(2.5, 5.0)
    ax.set_xlabel("")
    ax.axvline(3, color="gray", linestyle="--", linewidth=1.0, alpha=0.6)
    ax.grid(False)
    ax.invert_yaxis()

    legend_handles = [
        Line2D([0], [0], marker="o", color="none", markerfacecolor=course_colors["math"],
               markeredgecolor="white", markeredgewidth=0.8, markersize=7,
               label="Mean (GT)"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=course_colors["python"],
               markeredgecolor="white", markeredgewidth=0.8, markersize=7,
               label="Mean (Python)"),
        Line2D([0, 1], [0, 0], color=course_colors["math"], linewidth=2.6,
               label="90% CI (GT)"),
        Line2D([0, 1], [0, 0], color=course_colors["python"], linewidth=2.6,
               label="90% CI (Python)"),
        Line2D([0, 1], [0, 0], color=course_colors["math"], linewidth=1.2,
               label="95% CI (GT)"),
        Line2D([0, 1], [0, 0], color=course_colors["python"], linewidth=1.2,
               label="95% CI (Python)"),
    ]
    ax.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.32, -0.06),
        ncol=3,
        frameon=False,
        handletextpad=0.6,
        columnspacing=1.5,
    )
    plt.tight_layout()

    return fig, ax


def plot_likert_point_ci_by_behavior(
    dataframe: pd.DataFrame,
    items: list[str],
    group_order: list[str],
    group_colors: dict[str, str],
    group_labels: dict[str, str],
) -> tuple[plt.Figure, plt.Axes]:
    records = []
    for group in group_order:
        group_df = dataframe[dataframe["behavior_supergroup"] == group]
        for item in items:
            if item not in group_df.columns:
                continue
            series = group_df[item]
            series = series[series > 0].dropna()
            if series.empty:
                continue
            mean, ci90, ci95 = _mean_ci_bounds(series)
            records.append(
                {
                    "group": group,
                    "item": item,
                    "mean": mean,
                    "ci90": ci90,
                    "ci95": ci95,
                    "n": series.shape[0],
                }
            )

    if not records:
        raise ValueError("No valid Likert data for behavior groups.")

    plot_df = pd.DataFrame(records)
    manual_labels = {
        "Response accuracy": "Response\nAccuracy",
        "Question comprehension": "Question\nComprehension",
        "Response personalization": "Response\nPersonalization",
        "Learning progress awareness": "Learning Progress\nAwareness",
        "Course learning effectiveness": "Course Learning\nEffectiveness",
        "Assignment effectiveness": "Assignment\nEffectiveness",
        "Review effectiveness": "Review\nEffectiveness",
        "Exam effectiveness": "Exam\nEffectiveness",
        "Politeness": "Politeness",
        "Patience": "Patience",
        "Enjoyability": "Enjoyability",
        "Exploration encouragement": "Exploration\nEncouragement",
    }
    plot_df["item_wrapped"] = plot_df["item"].apply(lambda s: manual_labels.get(s, s))

    fig, ax = plt.subplots(figsize=(6.1, 7.0), dpi=300)

    item_order = list(dict.fromkeys(plot_df["item"].tolist()))
    y_base = {item: idx for idx, item in enumerate(item_order)}
    offset = 0.15

    for idx, group in enumerate(group_order):
        color = group_colors[group]
        sub = plot_df[plot_df["group"] == group]
        y_positions = [
            y_base[item] - offset if idx == 0 else y_base[item] + offset
            for item in sub["item"]
        ]
        ax.errorbar(
            sub["mean"],
            y_positions,
            xerr=sub["ci95"],
            fmt="none",
            ecolor=color,
            elinewidth=1.2,
            capsize=4,
            alpha=0.9,
        )
        ax.errorbar(
            sub["mean"],
            y_positions,
            xerr=sub["ci90"],
            fmt="o",
            color=color,
            ecolor=color,
            elinewidth=2.6,
            capsize=0,
            markersize=7,
            markeredgecolor="white",
            markeredgewidth=0.8,
        )

    ax.set_yticks([y_base[item] for item in item_order])
    ax.set_yticklabels([manual_labels.get(item, item) for item in item_order])
    ax.set_xlim(2.5, 5.0)
    ax.set_xlabel("")
    ax.axvline(3, color="gray", linestyle="--", linewidth=1.0, alpha=0.6)
    ax.grid(False)
    ax.invert_yaxis()

    legend_handles = []
    for group in group_order:
        color = group_colors[group]
        label = group_labels[group]
        legend_handles.append(
            Line2D([0], [0], marker="o", color="none", markerfacecolor=color,
                   markeredgecolor="white", markeredgewidth=0.8, markersize=7,
                   label=f"Mean ({label})")
        )
    for group in group_order:
        color = group_colors[group]
        label = group_labels[group]
        legend_handles.append(
            Line2D([0, 1], [0, 0], color=color, linewidth=2.6, label=f"90% CI ({label})")
        )
    for group in group_order:
        color = group_colors[group]
        label = group_labels[group]
        legend_handles.append(
            Line2D([0, 1], [0, 0], color=color, linewidth=1.2, label=f"95% CI ({label})")
        )

    ax.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.41, -0.06),
        ncol=3,
        frameon=False,
        handletextpad=0.6,
        columnspacing=1.5,
    )
    plt.tight_layout()

    return fig, ax


def _risk_delta_by_group(
    df_att: pd.DataFrame,
    *,
    risk_items: list[str],
    group_value: int,
) -> list[pd.Series]:
    group_df = df_att[df_att["group"] == group_value].copy()
    pre_mask = group_df["pre_risks"].apply(lambda v: v is not None)
    post_mask = group_df["post_risks"].apply(lambda v: v is not None)
    group_df = group_df[pre_mask & post_mask]

    deltas = []
    for item in risk_items:
        delta_series = (
            group_df["post_risks"].apply(lambda s: item in s).astype(int)
            - group_df["pre_risks"].apply(lambda s: item in s).astype(int)
        )
        deltas.append(delta_series)
    return deltas


def plot_risk_delta_by_group(
    df_att: pd.DataFrame,
    *,
    risk_items: list[str],
    risk_labels: dict[str, str],
    ax: plt.Axes | None = None,
    show_legend: bool = True,
) -> tuple[plt.Figure, plt.Axes]:
    deltas_control = _risk_delta_by_group(df_att, risk_items=risk_items, group_value=0)
    deltas_exp = _risk_delta_by_group(df_att, risk_items=risk_items, group_value=1)

    records = []
    for item, series in zip(risk_items, deltas_control):
        mean, ci90, ci95 = _mean_ci_bounds(series)
        records.append({"group": "control", "item": item, "mean": mean, "ci90": ci90, "ci95": ci95})
    for item, series in zip(risk_items, deltas_exp):
        mean, ci90, ci95 = _mean_ci_bounds(series)
        records.append({"group": "exp", "item": item, "mean": mean, "ci90": ci90, "ci95": ci95})

    plot_df = pd.DataFrame(records)

    if ax is None:
        fig, ax = plt.subplots(figsize=(3.0, 3.0), dpi=300)
    else:
        fig = ax.figure
    y = np.arange(len(risk_items))
    offset = 0.16

    control_color = "#6baed6"
    exp_color = "#31a354"

    for group, color, offset_sign in [
        ("control", control_color, -1),
        ("exp", exp_color, 1),
    ]:
        sub = plot_df[plot_df["group"] == group]
        y_positions = [y[idx] + offset_sign * offset for idx in range(len(risk_items))]
        ax.errorbar(
            sub["mean"],
            y_positions,
            xerr=sub["ci95"],
            fmt="none",
            ecolor=color,
            elinewidth=1.2,
            capsize=4,
            alpha=0.9,
        )
        ax.errorbar(
            sub["mean"],
            y_positions,
            xerr=sub["ci90"],
            fmt="o",
            color=color,
            ecolor=color,
            elinewidth=2.6,
            capsize=0,
            markersize=7,
            markeredgecolor="white",
            markeredgewidth=0.8,
        )

    ax.set_yticks(y)
    ax.set_yticklabels([risk_labels.get(item, item) for item in risk_items])
    ax.set_ylim(-0.6, float(len(risk_items)) - 0.4)
    ax.axvline(0, color="gray", linestyle="--", linewidth=1.0, alpha=0.6)
    mean_vals = [v for v in plot_df["mean"].tolist() if pd.notna(v)]
    ci95_vals = [v for v in plot_df["ci95"].tolist() if pd.notna(v)]
    if mean_vals:
        max_abs = max(
            [abs(m) + (ci95_vals[i] if i < len(ci95_vals) else 0.0) for i, m in enumerate(mean_vals)]
            + [0.1]
        )
    else:
        max_abs = 0.1
    ax.set_xlim(-max_abs * 1.6, max_abs * 1.6)
    ax.set_xlabel("")

    legend_handles = [
        Line2D([], [], linestyle="none", label="Control"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=control_color,
               markeredgecolor="white", markeredgewidth=0.8, markersize=7,
               label="Mean"),
        Line2D([0, 1], [0, 0], color=control_color, linewidth=2.6, label="90% CI"),
        Line2D([0, 1], [0, 0], color=control_color, linewidth=1.2, label="95% CI"),
        Line2D([], [], linestyle="none", label="Exp"),
        Line2D([0], [0], marker="o", color="none", markerfacecolor=exp_color,
               markeredgecolor="white", markeredgewidth=0.8, markersize=7,
               label="Mean"),
        Line2D([0, 1], [0, 0], color=exp_color, linewidth=2.6, label="90% CI"),
        Line2D([0, 1], [0, 0], color=exp_color, linewidth=1.2, label="95% CI"),
    ]
    if show_legend:
        ax.legend(
            handles=legend_handles,
            frameon=False,
            loc="upper center",
            bbox_to_anchor=(0.5, 1.18),
            ncol=3,
            columnspacing=1.4,
            handletextpad=0.6,
        )
        plt.tight_layout()

    return fig, ax


def plot_willingness_delta_violin_box(
    df_att: pd.DataFrame,
    *,
    title: str | None = None,
    out_ylabel: str = "Δ willingness",
    control_label: str = "Control",
    exp_label: str = "Experimental",
    control_color: str = CONTROL_COLOR,
    exp_color: str = EXP_COLOR,
    show_legend: bool = True,
    label_rotation: float = 0,
    ax: plt.Axes | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    delta = df_att["post_willingness"] - df_att["pre_willingness"]
    df_plot = df_att.copy()
    df_plot["delta"] = delta

    control = df_plot[df_plot["group"] == 0]["delta"].dropna().tolist()
    exp = df_plot[df_plot["group"] == 1]["delta"].dropna().tolist()

    data_list = [control, exp]
    labels = [control_label, exp_label]

    if ax is None:
        fig, ax = plt.subplots(figsize=(2.6, 3.0), dpi=300)
    else:
        fig = ax.figure
    positions = np.arange(1, len(data_list) + 1) * 1.0
    colors = [control_color, exp_color]

    violin_alpha = 0.78
    parts = ax.violinplot(
        data_list,
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

    box_colors = ["#6baed6", "#31a354"]
    box = ax.boxplot(
        data_list,
        positions=positions,
        widths=0.16,
        patch_artist=True,
        showfliers=False,
        whis=[5, 95],
    )
    for patch, c in zip(box["boxes"], box_colors):
        patch.set_facecolor(c)
        patch.set_edgecolor("#2F2F2F")
        patch.set_linewidth(1.0)
        patch.set_alpha(0.9)
    for med in box["medians"]:
        med.set_color("#222222")
        med.set_linewidth(1.6)
    for whisk in box["whiskers"]:
        whisk.set_color("#4D4D4D")
        whisk.set_linewidth(1.0)
    for cap in box["caps"]:
        cap.set_color("#4D4D4D")
        cap.set_linewidth(1.0)

    ax.set_xticks(positions)
    ax.set_xticklabels(labels, rotation=label_rotation, ha="center", color="black")
    ax.set_ylabel(out_ylabel)
    if title:
        ax.set_title(title)
    ax.axhline(0, color="gray", linestyle="--", linewidth=1.0, alpha=0.6)
    ax.grid(False)
    ax.set_xlim(0.4, float(len(data_list)) + 0.6)

    all_points = [x for sub in data_list for x in sub]
    if all_points:
        y_min, y_max = float(min(all_points)), float(max(all_points))
        span = max(1e-9, y_max - y_min)
        ax.set_ylim(y_min - 0.18 * span, y_max + 0.20 * span)

    if show_legend:
        legend_handles = [
            Patch(facecolor=control_color, edgecolor="none", label=control_label),
            Patch(facecolor=exp_color, edgecolor="none", label=exp_label),
        ]
        ax.legend(
            handles=legend_handles,
            frameon=False,
            loc="upper center",
            bbox_to_anchor=(0.5, 1.18),
            ncol=2,
            columnspacing=1.2,
            handletextpad=0.6,
        )

    if show_legend:
        plt.tight_layout()
    return fig, ax

_FEEDBACK_RUN_SOURCE = '# =========================\n# Block 1: Load and map data\n# =========================\ndf = load_postsurvey_data()\ndf = map_likert_scale_values(df)\ndf = map_multiselect_values(df)\nset_nature_style()\n\nprint("\\n" + "=" * 60)\nprint("Generating Feedback Analysis Plots")\nprint("=" * 60)\n\n \n\n\n# =========================\n# Block 2: Likert point + 95% CI plots\n# =========================\nlikert_items = [\n    "Response accuracy",\n    "Question comprehension",\n    "Response personalization",\n    "Learning progress awareness",\n    "Course learning effectiveness",\n    "Assignment effectiveness",\n    "Review effectiveness",\n    "Exam effectiveness",\n    "Politeness",\n    "Patience",\n    "Enjoyability",\n    "Exploration encouragement",\n]\n\nprint("\\nGenerating: feedback-likert-python-math.pdf")\nfig, _ = plot_likert_point_ci_by_course(\n    df,\n    items=likert_items,\n    title="LLM Feedback by Course (mean ± 95% CI)",\n    course_colors={"python": "#4C72B0", "math": "#DD8452"},\n)\n_save_and_maybe_show(fig, FIGURES_DIR / "feedback-likert-python-math.pdf")\n\n\n# =========================\n# Block 3: Multi-select pie plots\n# =========================\nif "目的_1" in df.columns:\n    fig, _ = plot_multi_select_pie(df, "目的_1")\n    _save_and_maybe_show(fig, FIGURES_DIR / "feedback-objectives.pdf")\n\nif "目的_3" in df.columns:\n    fig, _ = plot_multi_select_pie(df, "目的_3")\n    _save_and_maybe_show(fig, FIGURES_DIR / "feedback-methods.pdf")\n\nif "目的_2" in df.columns:\n    fig, _ = plot_multi_select_pie(df, "目的_2")\n    _save_and_maybe_show(fig, FIGURES_DIR / "feedback-effective-aspects.pdf")\n\n\n# =========================\n# Block 4: Pre/Post attitude shifts (control vs exp; python vs math)\n# =========================\ndf_att = load_prepost_attitudes()\n\ndf_math = df_att[df_att["course"] == "math"].copy()\ndf_python = df_att[df_att["course"] == "python"].copy()\n\nif not df_math.empty or not df_python.empty:\n    print("\\nGenerating: feedback-willingness-delta-combined.pdf")\n    fig_w, axes_w = plt.subplots(1, 2, figsize=(5.8, 3.0), dpi=300, sharey=True)\n    if not df_math.empty:\n        plot_willingness_delta_violin_box(\n            df_math,\n            title=None,\n            control_label="Control",\n            exp_label="Exp",\n            show_legend=False,\n            ax=axes_w[0],\n        )\n        axes_w[0].set_ylabel("Δ willingness")\n    if not df_python.empty:\n        plot_willingness_delta_violin_box(\n            df_python,\n            title=None,\n            control_label="Control",\n            exp_label="Exp",\n            show_legend=False,\n            ax=axes_w[1],\n        )\n        axes_w[1].set_ylabel("")\n    fig_w.tight_layout()\n    _save_and_maybe_show(fig_w, FIGURES_DIR / "feedback-willingness-delta-combined.pdf")\n\nif not df_math.empty or not df_python.empty:\n    print("\\nGenerating: feedback-risk-delta-combined.pdf")\n    fig_r, axes_r = plt.subplots(1, 2, figsize=(5.8, 3.0), dpi=300, sharey=True)\n    if not df_math.empty:\n        plot_risk_delta_by_group(\n            df_math,\n            risk_items=RISK_OVERLAP_ITEMS,\n            risk_labels=RISK_LABELS,\n            ax=axes_r[0],\n            show_legend=False,\n        )\n    if not df_python.empty:\n        plot_risk_delta_by_group(\n            df_python,\n            risk_items=RISK_OVERLAP_ITEMS,\n            risk_labels=RISK_LABELS,\n            ax=axes_r[1],\n            show_legend=False,\n        )\n\n    control_color = "#6baed6"\n    exp_color = "#31a354"\n    legend_handles = [\n        Line2D([], [], linestyle="none", label="Control"),\n        Line2D([0], [0], marker="o", color="none", markerfacecolor=control_color,\n               markeredgecolor="white", markeredgewidth=0.8, markersize=7,\n               label="  Mean"),\n        Line2D([0, 1], [0, 0], color=control_color, linewidth=2.6, label="  90% CI"),\n        Line2D([0, 1], [0, 0], color=control_color, linewidth=1.2, label="  95% CI"),\n        Line2D([], [], linestyle="none", label="Exp"),\n        Line2D([0], [0], marker="o", color="none", markerfacecolor=exp_color,\n               markeredgecolor="white", markeredgewidth=0.8, markersize=7,\n               label="  Mean"),\n        Line2D([0, 1], [0, 0], color=exp_color, linewidth=2.6, label="  90% CI"),\n        Line2D([0, 1], [0, 0], color=exp_color, linewidth=1.2, label="  95% CI"),\n    ]\n    leg = fig_r.legend(\n        handles=legend_handles,\n        frameon=False,\n        loc="center left",\n        bbox_to_anchor=(0.96, 0.5),\n        ncol=1,\n        columnspacing=1.2,\n        handletextpad=0.6,\n    )\n    if leg is not None:\n        control_label_color = _darken_color(control_color, 0.8)\n        exp_label_color = _darken_color(exp_color, 0.8)\n        for text in leg.get_texts():\n            if text.get_text() == "Control":\n                text.set_color(control_label_color)\n            elif text.get_text() == "Exp":\n                text.set_color(exp_label_color)\n    fig_r.tight_layout()\n    _save_and_maybe_show(fig_r, FIGURES_DIR / "feedback-risk-delta-combined.pdf")\n\nprint("\\n" + "=" * 60)\nprint("Feedback Analysis Complete")\nprint("=" * 60)\nprint("\\nDone!")\n'

def run_participant_feedback_analysis(*, figures_dir: Optional[Path] = None, show_figures: bool = False) -> dict[str, Any]:
    """Generate participant-feedback figures used by the main paper."""
    global FIGURES_DIR, SHOW_FIGURES
    FIGURES_DIR = Path(figures_dir) if figures_dir is not None else REPO_ROOT / "figures"
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    SHOW_FIGURES = bool(show_figures)
    exec(_FEEDBACK_RUN_SOURCE, globals(), globals())
    return {
        "output_files": [
            FIGURES_DIR / "feedback-likert-python-math.pdf",
            FIGURES_DIR / "feedback-objectives.pdf",
            FIGURES_DIR / "feedback-methods.pdf",
            FIGURES_DIR / "feedback-effective-aspects.pdf",
            FIGURES_DIR / "feedback-willingness-delta-combined.pdf",
            FIGURES_DIR / "feedback-risk-delta-combined.pdf",
        ]
    }
