"""Shared behavior-category rules used across analysis modules."""
from __future__ import annotations

from typing import Sequence


MATH_A1_PRECEDENCE: tuple[str, ...] = (
    "no_chat",
    "challenge_wrong",
    "fix_after_wrong",
    "ask_then_explain",
    "try_then_ask",
    "mindless_copy",
)

PYTHON_A1_PRECEDENCE: tuple[str, ...] = (
    "no_chat",
    "ask_then_explain",
    "try_then_ask",
    "mindless_copy",
)


def pick_python_a1_category(
    *,
    n_chats: int,
    tried_rate_problem: float,
    mindless_copy_rate_problem: float,
    ask_then_explain: bool,
    tried_threshold: float,
    copy_first_threshold: float,
    precedence: Sequence[str] = PYTHON_A1_PRECEDENCE,
) -> str:
    """Pick the mutually exclusive Python A1 behavior category."""

    def _match(cat: str) -> bool:
        if cat == "no_chat":
            return n_chats == 0
        if cat == "ask_then_explain":
            return n_chats > 0 and ask_then_explain
        if cat == "try_then_ask":
            return n_chats > 0 and tried_rate_problem >= tried_threshold
        if cat == "mindless_copy":
            return n_chats > 0 and mindless_copy_rate_problem >= copy_first_threshold
        raise ValueError(f"Unknown Python A1 category: {cat}")

    for cat in precedence:
        if _match(cat):
            return cat

    raise AssertionError(
        "Python A1 behavior did not match any configured category "
        f"(n_chats={n_chats}, tried_rate={tried_rate_problem:.3f}, "
        f"mindless_copy_rate={mindless_copy_rate_problem:.3f}, "
        f"ask_then_explain={ask_then_explain})"
    )


def pick_math_a1_category(
    *,
    n_chats: int,
    tried_rate_problem: float,
    mindless_copy_rate_problem: float,
    ask_then_explain: bool,
    challenge_wrong: bool,
    fix_after_wrong: bool,
    tried_threshold: float,
    copy_first_threshold: float,
    precedence: Sequence[str] = MATH_A1_PRECEDENCE,
) -> str:
    """Pick the mutually exclusive Math A1 behavior category.

    Verification/correction signals are prioritized first, matching the
    original main-paper Math A1 behavior profile. Mixed students who satisfy
    the active-trial threshold are assigned to active-trial before rote-adoption.
    """

    def _match(cat: str) -> bool:
        if cat == "no_chat":
            return n_chats == 0
        if cat == "challenge_wrong":
            return n_chats > 0 and challenge_wrong
        if cat == "fix_after_wrong":
            return n_chats > 0 and fix_after_wrong
        if cat == "ask_then_explain":
            return n_chats > 0 and ask_then_explain
        if cat == "mindless_copy":
            return n_chats > 0 and mindless_copy_rate_problem >= copy_first_threshold
        if cat == "try_then_ask":
            return n_chats > 0 and tried_rate_problem >= tried_threshold
        raise ValueError(f"Unknown Math A1 category: {cat}")

    for cat in precedence:
        if _match(cat):
            return cat

    raise AssertionError(
        "Math A1 behavior did not match any configured category "
        f"(n_chats={n_chats}, tried_rate={tried_rate_problem:.3f}, "
        f"mindless_copy_rate={mindless_copy_rate_problem:.3f}, "
        f"ask_then_explain={ask_then_explain}, challenge_wrong={challenge_wrong}, "
        f"fix_after_wrong={fix_after_wrong})"
    )
