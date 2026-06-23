"""Plots for participant-feedback survey results."""
from __future__ import annotations

import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from analyze.survey.feedback import COURSE_ORDER, MULTISELECT_QUESTIONS
from analyze.utils.display import relative_path
from analyze.survey.participant_feedback import (
    plot_likert_point_ci_by_course,
    plot_multi_select_pie,
    plot_risk_delta_by_group,
    plot_willingness_delta_violin_box,
)


BEHAVIOR_LABELS = {
    "control": "Control",
    "passive": "Limited engagement",
    "proactive_critic": "Proactive and critic",
}

BEHAVIOR_FILL_COLORS = {
    "control": "#d9d9d9",
    "passive": "#c6dbef",
    "proactive_critic": "#a1d99b",
}

BEHAVIOR_LINE_COLORS = {
    "control": "#8c8c8c",
    "passive": "#6baed6",
    "proactive_critic": "#31a354",
}
ATTITUDE_GROUP_ORDER = ["control", "passive", "proactive_critic"]
BEHAVIOR_GROUP_ORDER = ["passive", "proactive_critic"]


def save_and_maybe_show(fig: plt.Figure, output_path: Path, *, show: bool = False) -> None:
    """Save a figure and only open an interactive window when requested."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    print(f"Saved plot to: {relative_path(output_path)}")
    if show:
        plt.show()
    plt.close(fig)


def plot_self_report_by_observed_behavior(
    rate_df: pd.DataFrame,
    output_path: Path,
    *,
    show_figures: bool = False,
) -> None:
    behavior_order = BEHAVIOR_GROUP_ORDER
    question_order = [(col, label) for col, label, _options in MULTISELECT_QUESTIONS]
    fig, axes = plt.subplots(1, 2, figsize=(13.6, 3.05), dpi=300, sharex=True, sharey=True)
    axes = np.asarray(axes)
    for _row_idx, (question, _question_label) in enumerate(question_order):
        responses = (
            rate_df[rate_df["question"] == question]
            .groupby("response", sort=False)["count"]
            .sum()
            .sort_values(ascending=False)
        )
        response_order = responses[responses > 0].index.tolist()
        for col_idx, course in enumerate(COURSE_ORDER):
            ax = axes[col_idx]
            sub = rate_df[(rate_df["course"] == course) & (rate_df["question"] == question)]
            y = np.arange(len(response_order))
            height = 0.32
            for offset, behavior in enumerate(behavior_order):
                vals = []
                err_low = []
                err_high = []
                for response in response_order:
                    row = sub[
                        (sub["feedback_group"] == behavior)
                        & (sub["response"] == response)
                    ]
                    if row.empty:
                        vals.append(math.nan)
                        err_low.append(0.0)
                        err_high.append(0.0)
                        continue
                    rate = float(row.iloc[0]["rate"])
                    vals.append(rate)
                    err_low.append(max(0.0, rate - float(row.iloc[0]["ci95_low"])))
                    err_high.append(max(0.0, float(row.iloc[0]["ci95_high"]) - rate))
                ypos = y + (offset - 0.5) * height
                ax.barh(
                    ypos,
                    vals,
                    height=height,
                    xerr=[err_low, err_high],
                    color=BEHAVIOR_FILL_COLORS[behavior],
                    label=BEHAVIOR_LABELS.get(behavior, behavior),
                    alpha=0.9,
                    capsize=3,
                    linewidth=0.7,
                    edgecolor="white",
                    error_kw={
                        "elinewidth": 1.0,
                        "alpha": 0.9,
                        "ecolor": BEHAVIOR_LINE_COLORS[behavior],
                    },
                )
            ax.set_yticks(y)
            ax.set_yticklabels(response_order)
            ax.set_xlim(0, 1.02)
            ax.grid(False)
            ax.spines["top"].set_visible(False)
            ax.spines["right"].set_visible(False)
            ax.tick_params(axis="both", labelsize=12)
    axes[0].invert_yaxis()
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles=handles,
        labels=labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.0),
        ncol=2,
        frameon=False,
        fontsize=12,
        columnspacing=1.8,
        handlelength=2.2,
    )
    fig.tight_layout(rect=(0.0, 0.22, 1.0, 1.0))
    fig.text(
        0.5,
        0.15,
        "Proportion of students selecting each response",
        ha="center",
        va="center",
        fontsize=14,
    )
    save_and_maybe_show(fig, output_path, show=show_figures)


def plot_willingness_delta_by_behavior(
    df: pd.DataFrame,
    output_path: Path,
    *,
    show_figures: bool = False,
) -> None:
    fill_colors = [BEHAVIOR_FILL_COLORS[group] for group in ATTITUDE_GROUP_ORDER]
    line_colors = [BEHAVIOR_LINE_COLORS[group] for group in ATTITUDE_GROUP_ORDER]
    fig, axes = plt.subplots(2, 1, figsize=(6.2, 5.8), dpi=300, sharey=True)
    axes = np.asarray(axes)
    for ax, course in zip(axes, COURSE_ORDER):
        sub = df[df["course"] == course].copy()
        data_list = [
            sub[sub["feedback_group"] == group]["willingness_delta"].dropna().astype(float).tolist()
            for group in ATTITUDE_GROUP_ORDER
        ]
        positions = np.arange(1, len(data_list) + 1)
        parts = ax.violinplot(
            data_list,
            positions=positions,
            widths=0.52,
            showmeans=False,
            showmedians=False,
            showextrema=False,
        )
        for body, color in zip(parts["bodies"], fill_colors):
            body.set_facecolor(color)
            body.set_edgecolor(None)
            body.set_alpha(0.88)

        box = ax.boxplot(
            data_list,
            positions=positions,
            widths=0.12,
            patch_artist=True,
            showfliers=False,
            whis=[5, 95],
        )
        for patch, line_color in zip(box["boxes"], line_colors):
            patch.set_facecolor(line_color)
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

        ax.axhline(0, color="gray", linestyle="--", linewidth=1.0, alpha=0.6)
        ax.set_xticks(positions)
        ax.set_xticklabels([])
        ax.set_xlim(0.4, float(len(data_list)) + 0.6)
        ax.set_xlabel("")
        ax.grid(False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="both", labelsize=12)
    fig.text(
        0.065,
        0.54,
        r"$\Delta$ willingness",
        rotation=90,
        ha="center",
        va="center",
        fontsize=14,
    )
    handles = [
        Patch(facecolor=BEHAVIOR_FILL_COLORS[group], edgecolor="none", label=BEHAVIOR_LABELS[group])
        for group in ATTITUDE_GROUP_ORDER
    ]
    fig.legend(
        handles=handles,
        frameon=False,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.01),
        ncol=3,
        columnspacing=1.5,
        handlelength=1.8,
        handletextpad=0.6,
        fontsize=12,
    )
    fig.tight_layout(rect=(0.08, 0.1, 1.0, 1.0), h_pad=1.0)
    save_and_maybe_show(fig, output_path, show=show_figures)


def plot_risk_delta_by_behavior(
    summary_df: pd.DataFrame,
    output_path: Path,
    *,
    show_figures: bool = False,
) -> None:
    risk_df = summary_df[summary_df["metric"] != "willingness"].copy()
    metric_order = risk_df[["metric", "label"]].drop_duplicates().values.tolist()
    fig, axes = plt.subplots(2, 1, figsize=(7.0, 5.25), dpi=300, sharex=True)
    axes = np.asarray(axes)
    offsets = {"control": -0.20, "passive": 0.0, "proactive_critic": 0.20}
    y = np.arange(len(metric_order))
    for ax_idx, (ax, course) in enumerate(zip(axes, COURSE_ORDER)):
        sub = risk_df[risk_df["course"] == course]
        for group in ATTITUDE_GROUP_ORDER:
            vals = []
            err90_low = []
            err90_high = []
            err95_low = []
            err95_high = []
            for metric, _label in metric_order:
                row = sub[(sub["feedback_group"] == group) & (sub["metric"] == metric)]
                if row.empty:
                    vals.append(math.nan)
                    err90_low.append(0.0)
                    err90_high.append(0.0)
                    err95_low.append(0.0)
                    err95_high.append(0.0)
                    continue
                mean = float(row.iloc[0]["mean"])
                vals.append(mean)
                err90_low.append(max(0.0, mean - float(row.iloc[0]["ci90_low"])))
                err90_high.append(max(0.0, float(row.iloc[0]["ci90_high"]) - mean))
                err95_low.append(max(0.0, mean - float(row.iloc[0]["ci95_low"])))
                err95_high.append(max(0.0, float(row.iloc[0]["ci95_high"]) - mean))
            ypos = y + offsets[group]
            color = BEHAVIOR_LINE_COLORS[group]
            ax.errorbar(
                vals,
                ypos,
                xerr=[err95_low, err95_high],
                fmt="none",
                ecolor=color,
                elinewidth=0.95,
                capsize=3.5,
                alpha=0.85,
            )
            ax.errorbar(
                vals,
                ypos,
                xerr=[err90_low, err90_high],
                fmt="o",
                color=color,
                ecolor=color,
                elinewidth=2.15,
                capsize=0,
                markersize=5.8,
                markeredgecolor="white",
                markeredgewidth=0.8,
                label=BEHAVIOR_LABELS[group],
            )
        ax.set_yticks(y)
        ax.set_yticklabels([label for _metric, label in metric_order])
        ax.set_ylim(-0.6, float(len(metric_order)) - 0.4)
        ax.axvline(0, color="gray", linestyle="--", linewidth=1.0, alpha=0.6)
        ax.set_xlabel("")
        ax.grid(False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="both", labelsize=12)
        if ax_idx < len(axes) - 1:
            ax.tick_params(axis="x", bottom=False, labelbottom=False)
    axes[-1].set_xlabel(r"$\Delta$ perceived risk", fontsize=14)

    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color=BEHAVIOR_LINE_COLORS[group],
            markerfacecolor=BEHAVIOR_LINE_COLORS[group],
            markeredgecolor="white",
            markeredgewidth=0.8,
            linewidth=1.8,
            label=BEHAVIOR_LABELS[group],
        )
        for group in ATTITUDE_GROUP_ORDER
    ]
    fig.legend(
        handles=handles,
        frameon=False,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.01),
        ncol=3,
        columnspacing=1.4,
        handletextpad=0.6,
        fontsize=12,
    )
    fig.tight_layout(rect=(0.02, 0.08, 1.0, 1.0))
    save_and_maybe_show(fig, output_path, show=show_figures)
