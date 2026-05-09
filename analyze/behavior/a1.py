"""A1 behavior parsing and student-profile construction.

This module keeps the notebook-facing API organized around the data processing
task: read labeled chats, construct problem-level behavior features, and roll
them up to student behavior profiles.
"""
from __future__ import annotations

from analyze.behavior.a1_processing import (
    MATH_BEHAVIOR_LABELS,
    MATH_BEHAVIOR_ORDER,
    PY_BEHAVIOR_LABELS,
    PY_BEHAVIOR_ORDER,
    ChatLabel,
    ChatLabelMath,
    UserFeatures,
    UserFeaturesMath,
    _blanks_any_correct,
    _blanks_by_correct,
    _compute_single_problem_features_math,
    _infer_target_problems_from_labels,
    build_math_scores,
    build_user_problem_attempted_map,
    build_user_problem_attempted_map_math,
    build_user_problem_chats,
    build_user_problem_chats_math,
    compute_all_user_features,
    compute_all_user_features_math,
    compute_single_problem_features,
    infer_target_problems_from_labels,
    load_exclude_users,
    load_json,
    load_math_group_map,
    safe_float,
    use_canonical_behavior_labels,
    user_features_to_rows,
    user_features_to_rows_math,
)

# Public aliases for notebook readers. The underlying implementation uses
# leading underscores because these helpers began as script internals, but the
# notebooks now call them directly to show the blank-level math logic.
blanks_any_correct = _blanks_any_correct
blanks_by_correct = _blanks_by_correct
compute_single_problem_features_math = _compute_single_problem_features_math
infer_target_problems_from_labels_compat = _infer_target_problems_from_labels
