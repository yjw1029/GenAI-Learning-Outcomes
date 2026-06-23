"""Appendix-specific plotting helpers."""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from analyze.utils.display import relative_path
from analyze.stats.feature_screening import get_feature_display_names
from analyze.survey.participant_feedback import plot_multi_select_pie

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


def _mean_ci_bounds(series: pd.Series) -> tuple[float, float, float]:
    series = series.dropna()
    n = series.shape[0]
    if n < 2:
        mean = float(series.mean()) if n else math.nan
        return mean, 0.0, 0.0
    mean = float(series.mean())
    sd = float(series.std(ddof=1))
    se = sd / (n ** 0.5)
    ci90 = 1.645 * se
    ci95 = 1.96 * se
    return mean, ci90, ci95


def plot_likert_point_ci_by_course(
    dataframe: pd.DataFrame,
    items: list[str],
    title: str,
    course_colors: dict[str, str],
    xlim: tuple[float, float] = (1.0, 5.0),
) -> tuple[plt.Figure, plt.Axes, pd.DataFrame]:
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
        "HW1 Difficulty": "Assignment\nDifficulty",
        "HW2 Difficulty": "Exam\nDifficulty",
        "HW1 Time Sufficiency": "Assignment Time\nSufficiency",
        "HW2 Time Sufficiency": "Exam Time\nSufficiency",
        "Learning Time Sufficiency": "Learning Time\nSufficiency",
        "Review Helpfulness": "Review\nHelpfulness",
        "Assistant Ease of Use": "Assistant\nEase of Use",
    }

    fig, ax = plt.subplots(figsize=(6.2, 5.6), dpi=300)

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
    ax.set_xlim(xlim[0], xlim[1])
    ax.set_xlabel("")
    ax.axvline(3, color="gray", linestyle="--", linewidth=1.0, alpha=0.6)
    ax.grid(False)
    ax.invert_yaxis()

    legend_handles = [
        plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=course_colors["math"],
                   markeredgecolor="white", markeredgewidth=0.8, markersize=7,
                   label="Mean (GT)"),
        plt.Line2D([0], [0], marker="o", color="none", markerfacecolor=course_colors["python"],
                   markeredgecolor="white", markeredgewidth=0.8, markersize=7,
                   label="Mean (Python)"),
        plt.Line2D([0, 1], [0, 0], color=course_colors["math"], linewidth=2.6,
                   label="90% CI (GT)"),
        plt.Line2D([0, 1], [0, 0], color=course_colors["python"], linewidth=2.6,
                   label="90% CI (Python)"),
        plt.Line2D([0, 1], [0, 0], color=course_colors["math"], linewidth=1.2,
                   label="95% CI (GT)"),
        plt.Line2D([0, 1], [0, 0], color=course_colors["python"], linewidth=1.2,
                   label="95% CI (Python)"),
    ]
    ax.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.40, -0.08),
        ncol=3,
        frameon=False,
        handletextpad=0.6,
        columnspacing=1.5,
    )
    plt.tight_layout()

    return fig, ax, plot_df


def plot_directional_coeffs_combined(
    python_df: pd.DataFrame,
    math_df: pd.DataFrame,
    feature_order: list[str],
    output_path: Path,
    *,
    show: bool = False,
) -> None:
    python_features = set(python_df["feature"].tolist())
    math_features = set(math_df["feature"].tolist())
    available_features = python_features | math_features
    feature_order = [feat for feat in feature_order if feat in available_features]
    if not feature_order:
        raise ValueError("No overlapping features between SHAP importance and directional coefficients.")

    order_index = {name: idx for idx, name in enumerate(feature_order)}
    python_df = python_df.copy()
    math_df = math_df.copy()

    python_df["order"] = python_df["feature"].map(order_index)
    math_df["order"] = math_df["feature"].map(order_index)

    python_df = python_df.sort_values("order")
    math_df = math_df.sort_values("order")

    display_map = get_feature_display_names()
    y_labels = [display_map.get(feat, feat) for feat in feature_order]

    y_pos = np.arange(len(feature_order))
    height = 0.35

    fig, ax = plt.subplots(figsize=(6.8, 5.2), dpi=300)
    python_vals = [python_df.loc[python_df["feature"] == feat, "coef"].iloc[0] if feat in python_features else 0.0
                   for feat in feature_order]
    math_vals = [math_df.loc[math_df["feature"] == feat, "coef"].iloc[0] if feat in math_features else 0.0
                 for feat in feature_order]
    python_pvals = [python_df.loc[python_df["feature"] == feat, "p_value"].iloc[0] if feat in python_features else np.nan
                    for feat in feature_order]
    math_pvals = [math_df.loc[math_df["feature"] == feat, "p_value"].iloc[0] if feat in math_features else np.nan
                  for feat in feature_order]
    python_bars = ax.barh(
        y_pos - height / 2,
        python_vals,
        height=height,
        color="#4C72B0",
        label="Python",
    )
    math_bars = ax.barh(
        y_pos + height / 2,
        math_vals,
        height=height,
        color="#DD8452",
        label="GT",
    )
    ax.axvline(0, color="black", linewidth=1.0)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(y_labels)
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.invert_yaxis()
    ax.legend(
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.08),
        ncol=2,
        handletextpad=0.6,
        columnspacing=1.2,
    )

    max_abs = max(
        [abs(v) for v in python_vals + math_vals if not np.isnan(v)] + [1.0]
    )
    pad = 0.03 * max_abs

    def _format_p(pval: float) -> str:
        if np.isnan(pval):
            return "p=NA"
        if pval < 0.001:
            return "p<0.001"
        return f"p={pval:.3f}"

    def _annotate(bars, vals, pvals, text_color, x_anchor):
        for bar, val, pval in zip(bars, vals, pvals):
            if np.isnan(val):
                continue
            label = f"{val:+.2f} ({_format_p(pval)})"
            y = bar.get_y() + bar.get_height() / 2
            ax.text(x_anchor, y, label, va="center", ha="left", fontsize=8, color=text_color)

    x_anchor = 1.5 + pad
    _annotate(python_bars, python_vals, python_pvals, "#2F4B7C", x_anchor)
    _annotate(math_bars, math_vals, math_pvals, "#B24A00", x_anchor)
    plt.tight_layout()

    save_and_maybe_show(fig, output_path, show=show)


def save_and_maybe_show(fig: plt.Figure, out_path: Path, *, show: bool = False) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    print(f"Saved plot to: {relative_path(out_path)}")
    if show:
        plt.show()
    plt.close(fig)


def plot_feature_importance(importance_df: pd.DataFrame, output_path: Path, *, show: bool = False) -> None:
    fig, ax = plt.subplots(figsize=(6.4, 4.6), dpi=300)
    sns.barplot(data=importance_df, x="importance", y="feature_display", color="#4C72B0", ax=ax)
    ax.set_xlabel("")
    ax.set_ylabel("")
    plt.tight_layout()
    save_and_maybe_show(fig, output_path, show=show)


def plot_llm_accuracy_heatmap(pivot: pd.DataFrame, output_path: Path, *, show: bool = False) -> None:
    fig, ax = plt.subplots(figsize=(6.8, max(2.6, 0.35 * len(pivot.index))), dpi=300)
    sns.heatmap(
        pivot,
        ax=ax,
        vmin=0.0,
        vmax=1.0,
        cmap="YlGnBu",
        annot=True,
        fmt=".2f",
        linewidths=0.6,
        linecolor="white",
        cbar_kws={"label": "Accuracy"},
    )
    ax.set_xlabel("Difficulty")
    ax.set_ylabel("")
    fig.tight_layout()
    save_and_maybe_show(fig, output_path, show=show)
