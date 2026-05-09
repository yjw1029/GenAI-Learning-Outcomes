"""Plots for participant-feedback survey results."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from analyze.utils.display import relative_path
from analyze.survey.participant_feedback import (
    plot_likert_point_ci_by_course,
    plot_multi_select_pie,
    plot_risk_delta_by_group,
    plot_willingness_delta_violin_box,
)


def save_and_maybe_show(fig: plt.Figure, output_path: Path, *, show: bool = False) -> None:
    """Save a figure and only open an interactive window when requested."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    print(f"Saved plot to: {relative_path(output_path)}")
    if show:
        plt.show()
    plt.close(fig)
