"""Regression tests for behavior definitions shared by main and appendix analyses."""
from __future__ import annotations

import unittest
from unittest.mock import patch

import numpy as np

from analyze.behavior.a1_processing import (
    _build_behavior_mix_matrix,
    _participant_pattern_groups,
    _sort_behavior_mix_by_participant_pattern,
)
from analyze.behavior.category_rules import (
    MATH_A1_DISPLAY_ORDER,
    PYTHON_A1_DISPLAY_ORDER,
    behavior_supergroup,
)
from analyze.background.inequality import (
    categorize_capability_from_score,
    plot_equity_hw1,
)


class BehaviorCategoryRuleTests(unittest.TestCase):
    def test_python_display_order_uses_shared_supergroups(self) -> None:
        mapped = {
            category: behavior_supergroup(category, course_type="python")
            for category in PYTHON_A1_DISPLAY_ORDER
        }
        self.assertEqual(mapped["no_chat"], "passive")
        self.assertEqual(mapped["mindless_copy"], "passive")
        self.assertEqual(mapped["try_then_ask"], "proactive_critical")
        self.assertEqual(mapped["ask_then_explain"], "proactive_critical")

    def test_math_display_order_uses_shared_supergroups(self) -> None:
        mapped = {
            category: behavior_supergroup(category, course_type="math")
            for category in MATH_A1_DISPLAY_ORDER
        }
        self.assertEqual(mapped["no_chat"], "passive")
        self.assertEqual(mapped["mindless_copy"], "passive")
        for category in (
            "try_then_ask",
            "fix_after_wrong",
            "challenge_wrong",
            "ask_then_explain",
        ):
            self.assertEqual(mapped[category], "proactive_critical")

    def test_unknown_category_defaults_to_passive(self) -> None:
        self.assertEqual(
            behavior_supergroup("unknown", course_type="python"),
            "passive",
        )

    @patch("analyze.background.inequality.plot_equity_assignment_scores")
    def test_hw1_equity_plot_uses_main_interaction_spec(self, plot_mock) -> None:
        plot_equity_hw1("python", "math", "output.pdf", show=False)
        plot_mock.assert_called_once_with(
            "python",
            "math",
            "output.pdf",
            outcome_col="hw1_score",
            y_label="Assignment score",
            annotation="interaction",
            capability_categorizer=categorize_capability_from_score,
            report_interaction_stats=True,
            show=False,
        )


class BehaviorMixSortingTests(unittest.TestCase):
    def test_question_level_signals_map_to_the_matching_behavior_columns(self) -> None:
        features = {
            "abstention": {"n_chats": 0},
            "rote": {"n_chats": 1, "mindless_copy": True},
            "trial": {"n_chats": 1, "tried_any": True},
            "correction": {"n_chats": 1, "fix_after_wrong": True},
            "verification": {"n_chats": 1, "challenge_wrong": True},
        }

        matrix, users = _build_behavior_mix_matrix(
            user_problem_chats={key: {"problem": [value]} for key, value in features.items()},
            user_problem_attempted_without_chat={key: {} for key in features},
            target_problems=["problem"],
            problem_features_fn=lambda seq, _problem, _attempted: seq[0],
        )

        row_by_user = {user: matrix[idx] for idx, user in enumerate(users)}
        expected_columns = {
            "abstention": 0,
            "rote": 1,
            "trial": 2,
            "correction": 3,
            "verification": 4,
        }
        for user, column in expected_columns.items():
            expected = np.zeros(5)
            expected[column] = 1.0
            np.testing.assert_array_equal(row_by_user[user], expected)

    def test_sorts_by_participant_pattern_then_matching_question_share(self) -> None:
        behaviors = [
            "Abstention",
            "Rote-adoption",
            "Active-trial",
            "Error-correction",
            "Verification",
        ]
        users = ["trial-low", "rote", "trial-high", "abstain"]
        matrix = np.asarray(
            [
                [0.50, 0.00, 0.25, 0.00, 0.25],
                [0.25, 0.75, 0.00, 0.00, 0.00],
                [0.25, 0.00, 0.75, 0.00, 0.00],
                [1.00, 0.00, 0.00, 0.00, 0.00],
            ]
        )
        patterns = {
            "trial-low": "Active-trial",
            "rote": "Rote-adoption",
            "trial-high": "Active-trial",
            "abstain": "Abstention",
        }

        sorted_matrix, sorted_users, sorted_patterns = _sort_behavior_mix_by_participant_pattern(
            matrix, users, patterns, behaviors
        )

        self.assertEqual(sorted_users, ["abstain", "rote", "trial-high", "trial-low"])
        self.assertEqual(
            sorted_patterns,
            ["Abstention", "Rote-adoption", "Active-trial", "Active-trial"],
        )
        self.assertAlmostEqual(float(sorted_matrix[2, 2]), 0.75)
        self.assertEqual(
            _participant_pattern_groups(sorted_patterns, behaviors),
            [
                ("Abstention", 0, 1),
                ("Rote-adoption", 1, 2),
                ("Active-trial", 2, 4),
            ],
        )


if __name__ == "__main__":
    unittest.main()
