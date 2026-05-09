"""
Core data processing modules.

Provides shared functionality for loading, merging, and encoding
educational data needed by the remaining analysis scripts.
"""

from .data_processing import (
    load_presurvey_data,
    load_valid_users,
    load_capability_scores,
    load_homework_scores,
    merge_presurvey_to_df,
    prepare_covariates,
)

__all__ = [
    "load_presurvey_data",
    "load_valid_users",
    "load_capability_scores",
    "load_homework_scores",
    "merge_presurvey_to_df",
    "prepare_covariates",
]
