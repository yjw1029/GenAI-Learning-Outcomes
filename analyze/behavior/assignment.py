"""Assignment-score behavior plots used in the appendix."""
from __future__ import annotations

import math
import statistics
import warnings
from pathlib import Path
from typing import Any, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analyze.utils.display import relative_path
from analyze.background.inequality import (
    compute_math_a1_behavior_groups,
    compute_python_a1_behavior_groups,
)
from analyze.config import (
    MATH_HW1_PROBLEMS,
    MATH_HW2_PROBLEMS,
    MATH_SCORE_FILE,
    MATH_SCORE_MAP,
    PRESURVEY_FILE,
    PYTHON_SCORE_FILE,
    VALIDUSER_FILE,
)
from analyze.config.paths import CAPTEST_SCORE_FILE, PROJECT_ROOT
from analyze.core import (
    load_capability_scores,
    load_homework_scores,
    load_presurvey_data,
    load_valid_users,
    merge_presurvey_to_df,
    prepare_covariates,
)


def _data_path(*candidates: str) -> Path:
    for candidate in candidates:
        path = Path(candidate)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        if path.exists():
            return path
    return PROJECT_ROOT / candidates[0]


def _set_assignment_style() -> None:
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


def _try_import_stats():
    try:
        import scipy.stats  # type: ignore
    except Exception as exc:  # pragma: no cover - dependency failure path
        raise RuntimeError("Missing dependency: scipy") from exc
    return scipy.stats


def _perm_test_pvalue(
    x: list[float],
    y: list[float],
    *,
    n_perm: int = 10000,
    stat: str = "mean",
    seed: int = 42,
) -> float:
    rng = np.random.default_rng(seed)
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    combined = np.concatenate([x_arr, y_arr])
    n_x = len(x_arr)
    if stat == "median":
        obs = float(np.median(x_arr) - np.median(y_arr))
        stat_fn = np.median
    else:
        obs = float(np.mean(x_arr) - np.mean(y_arr))
        stat_fn = np.mean

    count = 0
    for _ in range(n_perm):
        rng.shuffle(combined)
        x_perm = combined[:n_x]
        y_perm = combined[n_x:]
        diff = float(stat_fn(x_perm) - stat_fn(y_perm))
        if abs(diff) >= abs(obs):
            count += 1
    return (count + 1) / (n_perm + 1)


def print_control_vs_exp_tests(
    *,
    control_hw: list[float],
    exp_hw_by_behavior: dict[str, list[float]],
) -> None:
    scipy_stats = _try_import_stats()

    def _clean(xs: list[float]) -> list[float]:
        out: list[float] = []
        for x in xs:
            try:
                v = float(x)
            except Exception:
                continue
            if not math.isnan(v):
                out.append(v)
        return out

    groups: dict[str, list[float]] = {"Control": _clean(control_hw)}
    for key, values in exp_hw_by_behavior.items():
        groups[key] = _clean(values)

    print("\nControl vs Experiment (behavior groups) hypothesis tests (raw p-values):")
    for key, values in groups.items():
        label = key.replace("\n", " ")
        if values:
            print(f"  {label}: n={len(values)} mean={statistics.mean(values):.3f} median={statistics.median(values):.3f}")
        else:
            print(f"  {label}: n=0")

    eligible = {key: values for key, values in groups.items() if len(values) >= 2}
    if len(eligible) >= 2:
        kw = scipy_stats.kruskal(*eligible.values(), nan_policy="omit")
        print(f"\n  Kruskal-Wallis across groups: H={float(kw.statistic):.4f}, p={float(kw.pvalue):.6g} (k={len(eligible)})")
    else:
        print("\n  Kruskal-Wallis: not enough eligible groups (need >=2 groups with n>=2).")

    control = groups.get("Control", [])
    if len(control) < 2:
        print("\n  Pairwise Brunner-Munzel vs Control: not enough control samples (need n>=2).")
        return

    print("\n  Pairwise Brunner-Munzel vs Control (two-sided, raw p-values):")
    print("\t".join(["group", "n_ctrl", "n_grp", "p_brunner_munzel", "p_perm_fallback"]))
    for key, values in groups.items():
        if key == "Control" or len(values) < 2:
            continue
        label = key.replace("\n", " ")
        # Brunner-Munzel can warn when ties make the variance estimate degenerate.
        # The p-value is then NaN, and the next branch reports a permutation fallback.
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            warnings.simplefilter("ignore", category=UserWarning)
            try:
                p_bm = float(scipy_stats.brunnermunzel(values, control, alternative="two-sided").pvalue)
            except TypeError:
                p_bm = float(scipy_stats.brunnermunzel(values, control).pvalue)
        p_perm = "NA"
        if math.isnan(p_bm):
            p_perm = f"{_perm_test_pvalue(values, control, n_perm=10000, stat='mean'):.6g}"
        print("\t".join([label, str(len(control)), str(len(values)), f"{p_bm:.6g}", str(p_perm)]))


def plot_control_vs_exp_behaviors_hw1(
    *,
    control_hw: list[float],
    exp_hw_by_behavior: dict[str, list[float]],
    exp_label_to_color: Optional[dict[str, Any]] = None,
    out_pdf: Optional[Path] = None,
    show: bool = True,
) -> None:
    _set_assignment_style()

    group_names = ["Control"] + list(exp_hw_by_behavior.keys())
    data_list = [control_hw] + [exp_hw_by_behavior[key] for key in exp_hw_by_behavior.keys()]

    filtered_data: list[list[float]] = []
    labels: list[str] = []
    for values, name in zip(data_list, group_names):
        clean_values = []
        for value in values:
            try:
                v = float(value)
            except Exception:
                continue
            if not math.isnan(v):
                clean_values.append(v)
        filtered_data.append(clean_values)
        labels.append(name)

    counts = [len(values) for values in filtered_data]
    means = [statistics.mean(values) if values else float("nan") for values in filtered_data]

    control_color = "#C9C9C9"
    exp_blues = ["#c6dbef", "#9ecae1", "#6baed6", "#2171b5"]
    colors: list[Any] = [control_color]
    for idx, name in enumerate(labels[1:]):
        if exp_label_to_color is not None and name in exp_label_to_color:
            colors.append(exp_label_to_color[name])
        else:
            colors.append(exp_blues[idx] if idx < len(exp_blues) else exp_blues[-1])

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

    for i, (values, pos) in enumerate(zip(filtered_data, positions)):
        if not values:
            continue
        q1, median, q3 = np.percentile(values, [25, 50, 75])
        low, high = np.percentile(values, [5, 95])
        span = float(np.max(values) - np.min(values) + 1e-9)
        gap = min(0.03 * span, 0.35 * max(1e-9, q3 - q1))
        gap_low = float(median - gap / 2)
        gap_high = float(median + gap / 2)

        ax.plot([pos, pos], [float(low), float(high)], color="#8A8A8A", linewidth=1.1, zorder=2, solid_capstyle="butt")

        try:
            from matplotlib.colors import to_rgba  # type: ignore

            bg = ax.get_facecolor()
            base = to_rgba(colors[i], 1.0)
            mask_color = tuple(violin_alpha * float(c) + (1.0 - violin_alpha) * float(b) for c, b in zip(base[:3], bg[:3])) + (1.0,)
        except Exception:
            mask_color = colors[i]

        eps = 0.01 * span
        ax.plot([pos, pos], [gap_low - eps, gap_high + eps], color=mask_color, linewidth=4.7, zorder=2.6, solid_capstyle="butt")

        lower_end = max(q1, median - gap / 2)
        upper_start = min(q3, median + gap / 2)
        if lower_end > q1:
            ax.plot([pos, pos], [q1, lower_end], color="#6A6A6A", linewidth=6.0, solid_capstyle="butt", zorder=3)
        if q3 > upper_start:
            ax.plot([pos, pos], [upper_start, q3], color="#6A6A6A", linewidth=6.0, solid_capstyle="butt", zorder=3)

    ax.set_xticks(positions)
    ax.set_xticklabels(labels, rotation=30, ha="right", color="black")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.set_xlabel("")
    ax.set_ylabel("Assignment Score")
    ax.set_xlim(0.4, float(len(filtered_data)) + 0.6)
    ax.grid(False)

    all_points = [x for values in filtered_data for x in values]
    span = None
    if all_points:
        y_min, y_max = float(min(all_points)), float(max(all_points))
        span = max(1e-9, y_max - y_min)
        ax.set_ylim(max(0.0, y_min - 0.18 * span), y_max + 0.20 * span)

    try:
        scipy_stats = _try_import_stats()
        control = filtered_data[0] if filtered_data else []
        if len(control) >= 2 and span is not None:
            def _fmt_p(p: float) -> str:
                if p < 0.005:
                    return "p<0.01"
                return f"p={p:.2f}"

            pairs: list[tuple[int, float]] = []
            for j in range(2, len(group_names) + 1):
                values = filtered_data[j - 1]
                if len(values) < 2:
                    continue
                # Suppress numerical warnings from degenerate tied samples; when the
                # test cannot estimate p directly, the permutation fallback below is used.
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=RuntimeWarning)
                    warnings.simplefilter("ignore", category=UserWarning)
                    try:
                        result = scipy_stats.brunnermunzel(values, control, alternative="two-sided")
                    except TypeError:
                        result = scipy_stats.brunnermunzel(values, control)
                p = float(result.pvalue)
                if math.isnan(p):
                    p = float(_perm_test_pvalue(values, control, n_perm=10000, stat="mean"))
                pairs.append((j, p))

            if all_points and pairs:
                y_min, y_max = float(min(all_points)), float(max(all_points))
                span = max(1e-9, y_max - y_min)
                y0, _ = ax.get_ylim()
                step = 0.12 * span
                ax.set_ylim(y0, y_max + 0.20 * span + 0.18 * span + step * len(pairs))
                line_y = y_max + 0.24 * span
                for j, p in sorted(pairs, key=lambda item: item[0]):
                    color = "#111111" if round(p, 2) <= 0.05 else "#9A9A9A"
                    x1 = float(positions[0])
                    x2 = float(positions[j - 1])
                    ax.plot([x1, x2], [line_y, line_y], lw=1.1, c=color, solid_capstyle="butt")
                    ax.text((x1 + x2) / 2, line_y + 0.010 * span, _fmt_p(p), ha="center", va="bottom", color=color, fontsize=9)
                    line_y += step
    except Exception:
        pass

    try:
        from matplotlib.patches import Patch  # type: ignore

        legend_labels = []
        for n, mean in zip(counts, means):
            mean_str = "NA" if math.isnan(mean) else f"{mean:.2f}"
            legend_labels.append(f"n={n}, μ={mean_str}")
        handles = [Patch(facecolor=color, edgecolor="none", label=label) for color, label in zip(colors, legend_labels)]
        ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.35), ncol=3, frameon=False, borderaxespad=0.0, fontsize=12)
        fig.tight_layout(rect=[0.0, 0.12, 1.0, 1.0])
    except Exception:
        fig.tight_layout()

    if out_pdf is not None:
        out_pdf.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_pdf, bbox_inches="tight")
        print("Saved figure:", relative_path(out_pdf))
    if show:
        plt.show()
    plt.close(fig)


def _load_hw1_tables() -> tuple[pd.DataFrame, pd.DataFrame]:
    presurvey = load_presurvey_data(PRESURVEY_FILE)
    python_df, math_df = load_valid_users(VALIDUSER_FILE)
    py_captest, math_captest = load_capability_scores(CAPTEST_SCORE_FILE)
    py_homework, math_homework = load_homework_scores(
        py_scores_file=PYTHON_SCORE_FILE,
        math_scores_file=MATH_SCORE_FILE,
        math_hw1_problems=list(MATH_HW1_PROBLEMS),
        math_hw2_problems=list(MATH_HW2_PROBLEMS),
        math_score_map=dict(MATH_SCORE_MAP),
    )

    python_df = merge_presurvey_to_df(python_df, presurvey, course_type="python")
    math_df = merge_presurvey_to_df(math_df, presurvey, course_type="math")
    python_df = python_df.merge(py_captest, on="username", how="left")
    math_df = math_df.merge(math_captest, on="username", how="left")
    python_df = python_df.merge(py_homework, on="username", how="left")
    math_df = math_df.merge(math_homework, on="username", how="left")
    python_df = prepare_covariates(python_df, course_type="python")
    math_df = prepare_covariates(math_df, course_type="math")
    return (
        python_df[python_df["hw1_score"] > 0].reset_index(drop=True),
        math_df[math_df["hw1_score"] > 0].reset_index(drop=True),
    )


def build_python_hw1_behavior_score_groups(python_df: pd.DataFrame) -> tuple[list[float], dict[str, list[float]]]:
    exp_user_ids = sorted(python_df.loc[python_df["group"] == 1, "username"].dropna().astype(str).unique().tolist())
    user_to_cat = compute_python_a1_behavior_groups(
        exp_user_ids,
        labels_path=_data_path("data/annotation/a1_chat_labels.json"),
        python_details_path=_data_path("data/annotation/python_details.json"),
        stage="a1",
        problem_prefix="py_",
        drop_unk_ask=True,
        problem_denom_policy="attempted_or_chatted",
        nochat_tried_if_attempted=True,
    )

    display_name = {
        "no_chat": "Unaided",
        "mindless_copy": "Rote-Adoption",
        "try_then_ask": "Active-Trial",
        "ask_then_explain": "Verification",
    }
    behavior_order = ["no_chat", "mindless_copy", "try_then_ask", "ask_then_explain"]
    exp_df = python_df[python_df["group"] == 1].copy()
    exp_df["a1_behavior_group"] = exp_df["username"].map(user_to_cat).fillna("no_chat")
    control_scores = python_df.loc[python_df["group"] == 0, "hw1_score"].dropna().astype(float).tolist()
    exp_scores = {
        display_name[cat]: exp_df.loc[exp_df["a1_behavior_group"] == cat, "hw1_score"].dropna().astype(float).tolist()
        for cat in behavior_order
    }
    return control_scores, exp_scores


def build_math_hw1_behavior_score_groups(math_df: pd.DataFrame) -> tuple[list[float], dict[str, list[float]]]:
    exp_user_ids = sorted(math_df.loc[math_df["group"] == 1, "username"].dropna().astype(str).unique().tolist())
    user_to_cat = compute_math_a1_behavior_groups(
        exp_user_ids,
        labels_path=_data_path("data/annotation/a1_chat_labels.json"),
        math_details_path=_data_path(
            "data/annotation/math_score_reviews_with_answers.json",
            "data/llm/math_score_reviews_with_answers.json",
        ),
        stage="a1",
        problem_prefix="math_",
        drop_unk_ask=True,
        problem_denom_policy="attempted_or_chatted",
        nochat_tried_if_attempted=True,
    )

    display_name = {
        "no_chat": "Unaided",
        "mindless_copy": "Rote-Adoption",
        "fix_after_wrong": "Error-Correction",
        "try_then_ask": "Active-Trial",
        "challenge_wrong": "Verification",
        "ask_then_explain": "Verification",
    }
    behavior_order = [
        "no_chat",
        "mindless_copy",
        "try_then_ask",
        "fix_after_wrong",
        "challenge_wrong",
        "ask_then_explain",
    ]
    exp_df = math_df[math_df["group"] == 1].copy()
    exp_df["a1_behavior_group"] = exp_df["username"].map(user_to_cat).fillna("no_chat")
    control_scores = math_df.loc[math_df["group"] == 0, "hw1_score"].dropna().astype(float).tolist()
    exp_scores: dict[str, list[float]] = {}
    for cat in behavior_order:
        label = display_name[cat]
        exp_scores.setdefault(label, []).extend(
            exp_df.loc[exp_df["a1_behavior_group"] == cat, "hw1_score"].dropna().astype(float).tolist()
        )
    return control_scores, exp_scores


def generate_hw1_behavior_assignment_plots(*, figures_dir: Path, show_figures: bool = False) -> dict[str, Any]:
    python_df, math_df = _load_hw1_tables()

    py_control, py_exp = build_python_hw1_behavior_score_groups(python_df)
    py_exp = {key: values for key, values in py_exp.items() if values}
    print_control_vs_exp_tests(control_hw=py_control, exp_hw_by_behavior=py_exp)
    plot_control_vs_exp_behaviors_hw1(
        control_hw=py_control,
        exp_hw_by_behavior=py_exp,
        exp_label_to_color={"Active-Trial": "#a1d99b", "Verification": "#31a354"},
        out_pdf=figures_dir / "a1_hw1_control_vs_exp_behavior.pdf",
        show=show_figures,
    )

    math_control, math_exp = build_math_hw1_behavior_score_groups(math_df)
    math_exp = {key: values for key, values in math_exp.items() if values}
    print_control_vs_exp_tests(control_hw=math_control, exp_hw_by_behavior=math_exp)
    plot_control_vs_exp_behaviors_hw1(
        control_hw=math_control,
        exp_hw_by_behavior=math_exp,
        exp_label_to_color={
            "Verification": "#238b45",
            "Error-Correction": "#74c476",
            "Active-Trial": "#a1d99b",
        },
        out_pdf=figures_dir / "a1_math_hw1_control_vs_exp_behavior.pdf",
        show=show_figures,
    )

    return {
        "python_n": int(len(python_df)),
        "math_n": int(len(math_df)),
        "output_files": [
            figures_dir / "a1_hw1_control_vs_exp_behavior.pdf",
            figures_dir / "a1_math_hw1_control_vs_exp_behavior.pdf",
        ],
    }
