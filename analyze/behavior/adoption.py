"""Direct-adoption and in-task LLM-accuracy diagnostics for A1 behavior."""
from __future__ import annotations

import csv
import json
import math
import sqlite3
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np

from analyze.utils.display import relative_path
from analyze.config import VALIDUSER_FILE
from analyze.core.data_processing import load_valid_users
from analyze.llm.evaluation import assign_difficulty_thresholds, compute_blank_points_map

REPO_ROOT = Path(__file__).resolve().parents[2]
FIGURES_DIR = REPO_ROOT / "figures"
SHOW_FIGURES = False

APP_A1_LABELS_PATH = REPO_ROOT / "data/annotation/a1_chat_labels.json"
APP_A1_PY_SCORES_PATH = REPO_ROOT / "data/annotation/python_scores.json"
APP_A1_PY_DETAILS_PATH = REPO_ROOT / "data/annotation/python_details.json"
APP_A1_MATH_DETAILS_PATH = REPO_ROOT / "data/llm/math_score_reviews_with_answers.json"
APP_A1_EXCLUDE_USERS_PATH = REPO_ROOT / "data/processed/exclude_user.csv"
APP_A1_BEHAVIORS_DB_PATH = REPO_ROOT / "data/processed/behaviors/merged_behaviors.db"

def _app_safe_get(d: Any, path: tuple[str, ...], default: Any = None) -> Any:
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def _app_parse_correct_flag(value: object) -> Optional[bool]:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        try:
            if math.isnan(float(value)):
                return None
        except Exception:
            return None
        return bool(int(value))
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"1", "y", "yes", "true"}:
            return True
        if v in {"0", "n", "no", "false"}:
            return False
    return None


def _app_wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n <= 0:
        return 0.0, 0.0
    p = k / float(n)
    denom = 1.0 + (z * z) / n
    center = (p + (z * z) / (2 * n)) / denom
    half = (z / denom) * math.sqrt((p * (1 - p) + (z * z) / (4 * n)) / n)
    return max(0.0, center - half), min(1.0, center + half)


def _app_order_difficulty_bins(bins: list[str]) -> list[str]:
    preferred = ["Easy", "Medium", "Hard"]
    ordered = [b for b in preferred if b in bins]
    if len(ordered) == len(bins):
        return ordered
    tail = [b for b in sorted(bins) if b not in ordered]
    return ordered + tail


def _app_apply_axes(ax, *, xlabel: str, ylabel: str) -> None:
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(False)


def _app_load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return obj if isinstance(obj, dict) else {}


def _app_load_excluded_users(path: Path) -> set[str]:
    if not path.exists():
        return set()
    out: set[str] = set()
    with path.open("r", encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            if not isinstance(row, dict):
                continue
            uid = str(row.get("username") or "").strip()
            if uid:
                out.add(uid)
    return out


def _app_infer_target_problems(labels_by_user: dict[str, Any], *, stage: str, prefix: str) -> list[str]:
    probs: set[str] = set()
    for _uid, user_blob in labels_by_user.items():
        if not isinstance(user_blob, dict):
            continue
        for _aid, rec in user_blob.items():
            if not isinstance(rec, dict):
                continue
            if stage and rec.get("stage") != stage:
                continue
            action = rec.get("action", "")
            if not (isinstance(action, str) and action.endswith("::chat")):
                continue
            problem = rec.get("problem") or (action.split("::", 1)[0] if "::" in action else action)
            if isinstance(problem, str) and problem.startswith(prefix):
                probs.add(problem)
    return sorted(probs)


def _app_load_hw1_entry_ts(db_path: Path, *, stage_name: str) -> dict[str, float]:
    import sqlite3

    if not db_path.exists():
        return {}
    con = sqlite3.connect(str(db_path))
    cur = con.cursor()
    cur.execute("SELECT username, timestamp, value FROM user_actions WHERE action=?", ("progress",))
    out: dict[str, float] = {}
    for username, ts, value in cur.fetchall():
        if not isinstance(username, str):
            continue
        try:
            ts_f = float(ts)
        except Exception:
            continue
        try:
            payload = json.loads(value) if isinstance(value, str) else value
        except Exception:
            payload = None
        if not isinstance(payload, dict):
            continue
        if str(payload.get("stage") or "").strip() != stage_name:
            continue
        if username not in out or ts_f < out[username]:
            out[username] = ts_f
    con.close()
    return out


def _app_is_no_tried_answer_copy(pre_tried: str, ask_type: str, ask_goal: str) -> bool:
    is_answer = (ask_type == "answer") or (ask_goal == "final_answer")
    return bool(is_answer and pre_tried == "n")


def _app_collect_python_chats(labels_by_user: dict[str, Any], uid: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    user_blob = labels_by_user.get(uid, {})
    if not isinstance(user_blob, dict):
        return rows
    for _aid, rec in user_blob.items():
        if not isinstance(rec, dict):
            continue
        if rec.get("stage") != "a1":
            continue
        action = rec.get("action", "")
        if not (isinstance(action, str) and action.endswith("::chat")):
            continue
        problem = rec.get("problem") or (action.split("::", 1)[0] if "::" in action else action)
        if not (isinstance(problem, str) and problem.startswith("py_")):
            continue
        label = rec.get("label") or {}
        pre_tried = str(_app_safe_get(label, ("pre", "tried"), "unk"))
        ask_type = str(_app_safe_get(label, ("ask", "type"), "unk"))
        ask_goal = str(_app_safe_get(label, ("ask", "goal"), "unk"))
        ask_correct = _app_parse_correct_flag(_app_safe_get(label, ("ask", "correct"), None))
        try:
            ts = float(rec.get("timestamp"))
        except Exception:
            ts = float("nan")
        rows.append(
            {
                "problem": problem,
                "timestamp": ts,
                "pre_tried": pre_tried,
                "ask_type": ask_type,
                "ask_goal": ask_goal,
                "ask_correct": ask_correct,
            }
        )
    rows.sort(key=lambda x: (str(x["problem"]), float(x["timestamp"])))
    return rows


def _app_collect_math_chats(labels_by_user: dict[str, Any], uid: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    user_blob = labels_by_user.get(uid, {})
    if not isinstance(user_blob, dict):
        return rows
    for _aid, rec in user_blob.items():
        if not isinstance(rec, dict):
            continue
        if rec.get("stage") != "a1":
            continue
        action = rec.get("action", "")
        if not (isinstance(action, str) and action.endswith("::chat")):
            continue
        problem = rec.get("problem") or (action.split("::", 1)[0] if "::" in action else action)
        if not (isinstance(problem, str) and problem.startswith("math_")):
            continue
        label = rec.get("label") or {}
        pre_tried = str(_app_safe_get(label, ("pre", "tried"), "unk"))
        ask_type = str(_app_safe_get(label, ("ask", "type"), "unk"))
        ask_goal = str(_app_safe_get(label, ("ask", "goal"), "unk"))
        ask_blanks = _app_safe_get(label, ("ask", "blanks"), {}) or {}
        post_blanks = _app_safe_get(label, ("post", "blanks"), {}) or {}
        pre_blanks = _app_safe_get(label, ("pre", "blanks"), {}) or {}
        try:
            ts = float(rec.get("timestamp"))
        except Exception:
            ts = float("nan")
        rows.append(
            {
                "problem": problem,
                "timestamp": ts,
                "pre_tried": pre_tried,
                "ask_type": ask_type,
                "ask_goal": ask_goal,
                "ask_blanks": ask_blanks if isinstance(ask_blanks, dict) else {},
                "post_blanks": post_blanks if isinstance(post_blanks, dict) else {},
                "pre_blanks": pre_blanks if isinstance(pre_blanks, dict) else {},
            }
        )
    rows.sort(key=lambda x: (str(x["problem"]), float(x["timestamp"])))
    return rows


def _app_run_plagiarism_figures(
    *,
    label: str,
    user_ids: list[str],
    target_problems: list[str],
    chats_by_user: dict[str, dict[str, list[dict[str, Any]]]],
    attempted_by_user_problem: dict[str, dict[str, bool]],
    active_trial_threshold: float,
    output_prefix: str,
) -> None:
    users_with_chat = [uid for uid in user_ids if sum(len(v) for v in chats_by_user.get(uid, {}).values()) > 0]
    user_plagiarism_ratio: list[float] = []
    for uid in users_with_chat:
        pmap = chats_by_user.get(uid, {})
        plag_count = 0
        for p in target_problems:
            seq = pmap.get(p, [])
            if any(_app_is_no_tried_answer_copy(c["pre_tried"], c["ask_type"], c["ask_goal"]) for c in seq):
                plag_count += 1
        if target_problems:
            user_plagiarism_ratio.append(plag_count / float(len(target_problems)))

    problem_plag_n = defaultdict(int)
    problem_denom_n = defaultdict(int)
    for uid in users_with_chat:
        pmap = chats_by_user.get(uid, {})
        amap = attempted_by_user_problem.get(uid, {})
        for p in target_problems:
            seq = pmap.get(p, [])
            has_chat = bool(seq)
            attempted = bool(amap.get(p, False))
            if has_chat or attempted:
                problem_denom_n[p] += 1
            if has_chat and any(_app_is_no_tried_answer_copy(c["pre_tried"], c["ask_type"], c["ask_goal"]) for c in seq):
                problem_plag_n[p] += 1

    problem_ratio = {
        p: (problem_plag_n.get(p, 0) / float(problem_denom_n[p]))
        for p in target_problems
        if problem_denom_n.get(p, 0) > 0
    }

    start_ts_by_user = _app_load_hw1_entry_ts(APP_A1_BEHAVIORS_DB_PATH, stage_name="完成作业 1")
    first_copy_minutes: list[float] = []
    for uid in users_with_chat:
        all_chats = [c for seq in chats_by_user.get(uid, {}).values() for c in seq if not math.isnan(float(c["timestamp"]))]
        if not all_chats:
            continue
        copy_chats = [c for c in all_chats if _app_is_no_tried_answer_copy(c["pre_tried"], c["ask_type"], c["ask_goal"])]
        if not copy_chats:
            continue
        start_ts = start_ts_by_user.get(uid, min(float(c["timestamp"]) for c in all_chats))
        first_ts = min(float(c["timestamp"]) for c in copy_chats)
        first_copy_minutes.append((first_ts - start_ts) / 60.0)

    bins = np.linspace(0, 1, 11)

    fig1, ax1 = plt.subplots(figsize=(3.6, 3.2), dpi=300)
    vals = [x for x in user_plagiarism_ratio if not math.isnan(x)]
    if vals:
        weights = np.full(len(vals), 1.0 / len(vals), dtype=float)
        hist_vals, edges = np.histogram(vals, bins=bins, weights=weights)
        widths = np.diff(edges)
        lefts = edges[:-1]
        ax1.bar(lefts, hist_vals, width=widths, align="edge", color="#9ecae1", edgecolor="white", linewidth=0.8)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(bottom=0)
    _app_apply_axes(ax1, xlabel="Problem Rote-Adoption Rate", ylabel="Participant Proportion")
    fig1.tight_layout()
    out_fig1 = FIGURES_DIR / f"{output_prefix}_user_plagiarism_ratio.pdf"
    fig1.savefig(out_fig1, dpi=300, bbox_inches="tight")
    print(f"[Appendix][{label}] Saved: {relative_path(out_fig1)}")
    if SHOW_FIGURES:
        plt.show()
    plt.close(fig1)

    fig2, ax2 = plt.subplots(figsize=(4.8, 3.2), dpi=300)
    order = target_problems
    ys = [problem_ratio.get(p, 0.0) for p in order]
    xs = np.arange(len(order))
    xlabels = [p.split("/")[-1] if "/" in p else p for p in order]
    ax2.bar(xs, ys, color="#AECDE1", edgecolor="white", linewidth=0.8)
    ax2.set_ylim(0, 1.0)
    ax2.set_xticks(xs)
    ax2.set_xticklabels(xlabels, rotation=0, ha="center")
    _app_apply_axes(ax2, xlabel="Problem", ylabel="Direct Adoption Rate")
    fig2.tight_layout()
    out_fig2 = FIGURES_DIR / f"{output_prefix}_problem_plagiarism_ratio.pdf"
    fig2.savefig(out_fig2, dpi=300, bbox_inches="tight")
    print(f"[Appendix][{label}] Saved: {relative_path(out_fig2)}")
    if SHOW_FIGURES:
        plt.show()
    plt.close(fig2)

    fig3, ax3 = plt.subplots(figsize=(4.8, 3.2), dpi=300)
    within = sorted([min(x, 20.0) for x in first_copy_minutes if 0.0 <= x <= 20.0])
    xs_ev = np.array(within, dtype=float) if within else np.array([], dtype=float)
    n_total = len(users_with_chat)
    ax3.axvline(20, color="#666666", linewidth=1.0, linestyle="--")
    ax3.set_xlim(0, 20)
    ax3.set_ylim(0, 1.0)
    _app_apply_axes(ax3, xlabel="Time To First Direct Adoption (Min)", ylabel="Cumulative Proportion")
    if n_total > 0 and len(xs_ev) > 0:
        ys_ev = np.arange(1, len(xs_ev) + 1, dtype=float) / float(n_total)
        xs_plot = np.concatenate(([0.0], xs_ev, [20.0]))
        ys_plot = np.concatenate(([0.0], ys_ev, [ys_ev[-1]]))
        ax3.step(xs_plot, ys_plot, where="post", color="#AECDE1", linewidth=2.2)
        ax3.vlines(xs_ev, 0.0, 0.03, color="#AECDE1", linewidth=1.0, alpha=0.9)
    else:
        ax3.step([0.0, 20.0], [0.0, 0.0], where="post", color="#AECDE1", linewidth=2.2)
    fig3.tight_layout()
    out_fig3 = FIGURES_DIR / f"{output_prefix}_first_no_tried_copy_time_cdf.pdf"
    fig3.savefig(out_fig3, dpi=300, bbox_inches="tight")
    print(f"[Appendix][{label}] Saved: {relative_path(out_fig3)}")
    if SHOW_FIGURES:
        plt.show()
    plt.close(fig3)


def _app_run_python_llm_accuracy(labels_by_user: dict[str, Any], details_by_user: dict[str, Any], user_ids: list[str]) -> None:
    problem_max_score: dict[str, int] = {}
    for uid in user_ids:
        drec = details_by_user.get(uid, {})
        if not isinstance(drec, dict):
            continue
        probs = drec.get("problems", {})
        if not isinstance(probs, dict):
            continue
        for p, prec in probs.items():
            if not isinstance(prec, dict):
                continue
            ms = prec.get("max_score")
            try:
                ms_i = int(ms)
            except Exception:
                continue
            if p not in problem_max_score:
                problem_max_score[p] = ms_i

    def _diff(ms: Optional[int]) -> Optional[str]:
        if ms is None:
            return None
        if ms in (1, 2):
            return "Easy"
        if ms == 3:
            return "Medium"
        if ms in (4, 5):
            return "Hard"
        return None

    diff_bins = ["Easy", "Medium", "Hard"]
    counts: dict[str, tuple[int, int]] = {b: (0, 0) for b in diff_bins}
    for uid in user_ids:
        for c in _app_collect_python_chats(labels_by_user, uid):
            flag = c["ask_correct"]
            if flag is None:
                continue
            d = _diff(problem_max_score.get(str(c["problem"])))
            if d is None:
                continue
            k, n = counts[d]
            counts[d] = (k + (1 if bool(flag) else 0), n + 1)

    fig, ax = plt.subplots(figsize=(3.6, 3.2), dpi=300)
    x = np.arange(len(diff_bins))
    acc_vals, err_low, err_high = [], [], []
    for b in diff_bins:
        k, n = counts[b]
        acc = (k / n) if n else 0.0
        lo, hi = _app_wilson_ci(k, n)
        acc_vals.append(acc)
        err_low.append(acc - lo)
        err_high.append(hi - acc)
    ax.bar(x, acc_vals, color="#9ecae1", edgecolor="white", linewidth=0.8)
    ax.errorbar(x, acc_vals, yerr=[err_low, err_high], fmt="none", ecolor="#2b2b2b", capsize=3, lw=1.0)
    ax.set_xticks(x)
    ax.set_xticklabels(diff_bins)
    ax.set_ylim(0.0, 1.0)
    _app_apply_axes(ax, xlabel="Difficulty", ylabel="Accuracy")
    fig.tight_layout()
    out = FIGURES_DIR / "a1_py_llm_accuracy_by_difficulty.pdf"
    fig.savefig(out, dpi=300, bbox_inches="tight")
    print(f"[Appendix][Python] Saved: {relative_path(out)}")
    if SHOW_FIGURES:
        plt.show()
    plt.close(fig)


def _app_merge_final_math_blanks(seq: list[dict[str, Any]]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for c in seq:
        pre = c.get("pre_blanks", {})
        post = c.get("post_blanks", {})
        if isinstance(pre, dict):
            merged.update(pre)
        if isinstance(post, dict):
            merged.update(post)
    return merged


def _app_run_math_llm_accuracy_and_correction(labels_by_user: dict[str, Any], user_ids: list[str]) -> None:
    chats_by_user_problem: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for uid in user_ids:
        chats = _app_collect_math_chats(labels_by_user, uid)
        by_prob: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for c in chats:
            by_prob[str(c["problem"])].append(c)
        chats_by_user_problem[uid] = {p: sorted(v, key=lambda x: float(x["timestamp"])) for p, v in by_prob.items()}

    blank_points = compute_blank_points_map()
    blank_difficulty = assign_difficulty_thresholds(blank_points, easy_max=0.5, medium_max=1.5)
    diff_bins = _app_order_difficulty_bins(sorted(set(blank_difficulty.values())))

    llm_counts: dict[str, tuple[int, int]] = {b: (0, 0) for b in diff_bins}
    for _uid, pmap in chats_by_user_problem.items():
        for prob, seq in pmap.items():
            for c in seq:
                ask_blanks = c.get("ask_blanks", {})
                if not isinstance(ask_blanks, dict):
                    continue
                for bid, v in ask_blanks.items():
                    if not isinstance(v, dict):
                        continue
                    flag = _app_parse_correct_flag(v.get("correct"))
                    if flag is None:
                        continue
                    d = blank_difficulty.get((prob, str(bid)))
                    if d is None:
                        continue
                    k, n = llm_counts[d]
                    llm_counts[d] = (k + (1 if flag else 0), n + 1)

    fig_a, ax_a = plt.subplots(figsize=(3.6, 3.2), dpi=300)
    x = np.arange(len(diff_bins))
    acc_vals, err_low, err_high = [], [], []
    for b in diff_bins:
        k, n = llm_counts.get(b, (0, 0))
        acc = (k / n) if n else 0.0
        lo, hi = _app_wilson_ci(k, n)
        acc_vals.append(acc)
        err_low.append(acc - lo)
        err_high.append(hi - acc)
    ax_a.bar(x, acc_vals, color="#9ecae1", edgecolor="white", linewidth=0.8)
    ax_a.errorbar(x, acc_vals, yerr=[err_low, err_high], fmt="none", ecolor="#2b2b2b", capsize=3, lw=1.0)
    ax_a.set_xticks(x)
    ax_a.set_xticklabels(diff_bins)
    ax_a.set_ylim(0.0, 1.0)
    _app_apply_axes(ax_a, xlabel="Difficulty", ylabel="Accuracy")
    fig_a.tight_layout()
    out_acc = FIGURES_DIR / "a1_math_llm_accuracy_by_difficulty.pdf"
    fig_a.savefig(out_acc, dpi=300, bbox_inches="tight")
    print(f"[Appendix][Math] Saved: {relative_path(out_acc)}")
    if SHOW_FIGURES:
        plt.show()
    plt.close(fig_a)

    wrong_outcomes = {b: {"llm_correct_aligned": 0, "self_corrected": 0, "error_aligned": 0, "total": 0} for b in diff_bins}
    correct_not_adopted = {b: {"misled_by_wrong": 0, "self_wrong": 0, "total_with_llm_correct": 0} for b in diff_bins}
    for _uid, pmap in chats_by_user_problem.items():
        for prob, seq in pmap.items():
            if not seq:
                continue
            ever_wrong: dict[str, bool] = defaultdict(bool)
            ever_correct: dict[str, bool] = defaultdict(bool)
            for c in seq:
                ask_blanks = c.get("ask_blanks", {})
                if not isinstance(ask_blanks, dict):
                    continue
                for bid, v in ask_blanks.items():
                    if not isinstance(v, dict):
                        continue
                    flag = _app_parse_correct_flag(v.get("correct"))
                    if flag is None:
                        continue
                    if flag:
                        ever_correct[str(bid)] = True
                    else:
                        ever_wrong[str(bid)] = True
            final_blanks = _app_merge_final_math_blanks(seq)
            for bid, was_wrong in ever_wrong.items():
                if not was_wrong:
                    continue
                d = blank_difficulty.get((prob, bid))
                if d is None:
                    continue
                v = final_blanks.get(bid)
                if not isinstance(v, dict):
                    continue
                final_flag = _app_parse_correct_flag(v.get("correct"))
                if final_flag is None:
                    continue
                wrong_outcomes[d]["total"] += 1
                if final_flag:
                    if ever_correct.get(bid, False):
                        wrong_outcomes[d]["llm_correct_aligned"] += 1
                    else:
                        wrong_outcomes[d]["self_corrected"] += 1
                else:
                    wrong_outcomes[d]["error_aligned"] += 1
            for bid, was_correct in ever_correct.items():
                if not was_correct:
                    continue
                d = blank_difficulty.get((prob, bid))
                if d is None:
                    continue
                v = final_blanks.get(bid)
                if not isinstance(v, dict):
                    continue
                final_flag = _app_parse_correct_flag(v.get("correct"))
                if final_flag is None:
                    continue
                correct_not_adopted[d]["total_with_llm_correct"] += 1
                if not final_flag:
                    if ever_wrong.get(bid, False):
                        correct_not_adopted[d]["misled_by_wrong"] += 1
                    else:
                        correct_not_adopted[d]["self_wrong"] += 1

    fig_c, ax_c = plt.subplots(figsize=(3.6, 3.2), dpi=300)
    bottoms = np.zeros(len(diff_bins), dtype=float)
    x = np.arange(len(diff_bins))
    for key, label, color in [
        ("llm_correct_aligned", "LLM-Consistent Correction", "#9ECAE1"),
        ("self_corrected", "Self-Correction", "#74C476"),
    ]:
        vals = []
        for b in diff_bins:
            d = wrong_outcomes[b]
            n = d["total"]
            vals.append((d[key] / n) if n > 0 else 0.0)
        ax_c.bar(x, vals, bottom=bottoms, color=color, edgecolor="white", linewidth=0.7, label=label)
        bottoms += np.array(vals, dtype=float)
    ax_c.set_xticks(x)
    ax_c.set_xticklabels(diff_bins)
    ax_c.set_ylim(0.0, 0.7)
    _app_apply_axes(ax_c, xlabel="Difficulty", ylabel="Correction Ratio")
    ax_c.legend(frameon=False, loc="upper right", bbox_to_anchor=(1.0, 1.05), fontsize=9)
    fig_c.tight_layout()
    out_corr = FIGURES_DIR / "a1_math_llm_wrong_outcome_by_difficulty.pdf"
    fig_c.savefig(out_corr, dpi=300, bbox_inches="tight")
    print(f"[Appendix][Math] Saved: {relative_path(out_corr)}")
    if SHOW_FIGURES:
        plt.show()
    plt.close(fig_c)

    fig_n, ax_n = plt.subplots(figsize=(3.6, 3.2), dpi=300)
    bottoms = np.zeros(len(diff_bins), dtype=float)
    for key, label, color in [
        ("misled_by_wrong", "LLM-Error-Influenced Non-Adoption", "#FC9272"),
        ("self_wrong", "Self-Origin Non-Adoption", "#9ECAE1"),
    ]:
        vals = []
        for b in diff_bins:
            d = correct_not_adopted[b]
            n = d["total_with_llm_correct"]
            vals.append((d[key] / n) if n > 0 else 0.0)
        ax_n.bar(x, vals, bottom=bottoms, color=color, edgecolor="white", linewidth=0.7, label=label)
        bottoms += np.array(vals, dtype=float)
    ax_n.set_xticks(x)
    ax_n.set_xticklabels(diff_bins)
    ax_n.set_ylim(0.0, 0.7)
    _app_apply_axes(ax_n, xlabel="Difficulty", ylabel="Non-adoption Ratio")
    ax_n.legend(frameon=False, loc="upper right", bbox_to_anchor=(1.0, 1.05), fontsize=9)
    fig_n.tight_layout()
    out_non = FIGURES_DIR / "a1_math_llm_correct_not_adopted_by_difficulty.pdf"
    fig_n.savefig(out_non, dpi=300, bbox_inches="tight")
    print(f"[Appendix][Math] Saved: {relative_path(out_non)}")
    if SHOW_FIGURES:
        plt.show()
    plt.close(fig_n)


def run_a1_appendix_analyses() -> None:
    labels = _app_load_json(APP_A1_LABELS_PATH)
    py_scores = _app_load_json(APP_A1_PY_SCORES_PATH)
    py_details = _app_load_json(APP_A1_PY_DETAILS_PATH)
    math_details = _app_load_json(APP_A1_MATH_DETAILS_PATH)
    excluded = _app_load_excluded_users(APP_A1_EXCLUDE_USERS_PATH)

    py_users = sorted(
        [
            uid
            for uid, s in py_scores.items()
            if isinstance(s, dict) and s.get("group") == "Experiment" and uid not in excluded
        ]
    )
    py_target = _app_infer_target_problems(labels, stage="a1", prefix="py_")
    py_chats_by_user_problem: dict[str, dict[str, list[dict[str, Any]]]] = {}
    py_attempted: dict[str, dict[str, bool]] = {}
    for uid in py_users:
        chats = _app_collect_python_chats(labels, uid)
        by_prob: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for c in chats:
            by_prob[str(c["problem"])].append(c)
        py_chats_by_user_problem[uid] = {p: sorted(v, key=lambda x: float(x["timestamp"])) for p, v in by_prob.items()}
        drec = py_details.get(uid, {}) if isinstance(py_details.get(uid, {}), dict) else {}
        probs = drec.get("problems", {}) if isinstance(drec.get("problems", {}), dict) else {}
        py_attempted[uid] = {
            p: (isinstance(probs.get(p, {}), dict) and probs.get(p, {}).get("user_answer") is not None)
            for p in py_target
        }

    _app_run_plagiarism_figures(
        label="Python",
        user_ids=py_users,
        target_problems=py_target,
        chats_by_user=py_chats_by_user_problem,
        attempted_by_user_problem=py_attempted,
        active_trial_threshold=0.25,
        output_prefix="a1",
    )
    _app_run_python_llm_accuracy(labels, py_details, py_users)

    _py_valid, math_valid = load_valid_users(VALIDUSER_FILE)
    math_users = sorted(
        [
            str(uid)
            for uid in math_valid.loc[math_valid["group"] == 1, "username"].dropna().astype(str).tolist()
            if str(uid) not in excluded
        ]
    )
    math_target = _app_infer_target_problems(labels, stage="a1", prefix="math_")
    math_chats_by_user_problem: dict[str, dict[str, list[dict[str, Any]]]] = {}
    math_attempted: dict[str, dict[str, bool]] = {}
    for uid in math_users:
        chats = _app_collect_math_chats(labels, uid)
        by_prob: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for c in chats:
            by_prob[str(c["problem"])].append(c)
        math_chats_by_user_problem[uid] = {p: sorted(v, key=lambda x: float(x["timestamp"])) for p, v in by_prob.items()}
        drec = math_details.get(uid, {}) if isinstance(math_details.get(uid, {}), dict) else {}
        math_attempted[uid] = {
            p: (isinstance(drec.get(p, {}), dict) and drec.get(p, {}).get("user_answer") is not None)
            for p in math_target
        }

    _app_run_plagiarism_figures(
        label="Math",
        user_ids=math_users,
        target_problems=math_target,
        chats_by_user=math_chats_by_user_problem,
        attempted_by_user_problem=math_attempted,
        active_trial_threshold=0.5,
        output_prefix="a1_math",
    )
    _app_run_math_llm_accuracy_and_correction(labels, math_users)


def generate_a1_behavior_diagnostics(*, figures_dir: Path | None = None, show_figures: bool = False) -> None:
    """Generate direct-adoption and in-task LLM-accuracy appendix figures."""
    global FIGURES_DIR, SHOW_FIGURES
    FIGURES_DIR = Path(figures_dir) if figures_dir is not None else REPO_ROOT / "figures"
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    SHOW_FIGURES = bool(show_figures)
    run_a1_appendix_analyses()
