"""Regression tests for appendix assignment-score sample construction."""
from __future__ import annotations

import unittest

from analyze.behavior.assignment import (
    _load_hw1_tables,
    build_python_hw1_behavior_score_groups,
)


class AssignmentSampleTests(unittest.TestCase):
    def test_python_hw1_keeps_valid_zero_scores(self) -> None:
        python_df, _math_df = _load_hw1_tables()
        self.assertEqual(python_df.groupby("group").size().to_dict(), {0: 27, 1: 54})
        self.assertEqual(int((python_df["hw1_score"] == 0).sum()), 5)

    def test_python_hw1_group_counts_match_main_population(self) -> None:
        python_df, _math_df = _load_hw1_tables()
        control_scores, experiment_scores = build_python_hw1_behavior_score_groups(
            python_df
        )
        self.assertEqual(len(control_scores), 27)
        self.assertEqual(len(experiment_scores["Abstention"]), 5)
        self.assertEqual(sum(map(len, experiment_scores.values())), 54)


if __name__ == "__main__":
    unittest.main()
