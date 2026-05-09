"""Regression-style statistical summaries used by the notebooks."""
from __future__ import annotations

from analyze.background.inequality import (
    _run_binned_numeric_model,
    compute_explained_variance_behavior_metrics,
    report_behavior_prediction_from_university_and_prior,
    report_explained_variance_behavior,
)

run_binned_numeric_model = _run_binned_numeric_model
