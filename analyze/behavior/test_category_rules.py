"""Regression tests for behavior definitions shared by main and appendix analyses."""
from __future__ import annotations

import unittest
from unittest.mock import patch

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


if __name__ == "__main__":
    unittest.main()
