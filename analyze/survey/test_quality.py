"""Survey loaders and response mapping for appendix test-quality analysis."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from analyze.config import POSTSURVEY_FILE, VALIDUSER_FILE
from analyze.core.data_processing import load_valid_users

def load_postsurvey_data(include_control: bool = False) -> pd.DataFrame:
    with open(POSTSURVEY_FILE, "r", encoding="utf-8") as f:
        postsurvey = json.load(f)

    data = []
    for username, survey in postsurvey.items():
        row = {"username": username}
        row.update(survey)
        data.append(row)

    df = pd.DataFrame(data)

    python_df, math_df = load_valid_users(VALIDUSER_FILE)
    valid_users_df = pd.concat([python_df, math_df], ignore_index=True)
    if not include_control:
        valid_users_df = valid_users_df[valid_users_df["group"] == 1].copy()

    df = df.merge(valid_users_df[["username", "group", "course"]], on="username", how="inner")
    return df


def map_test_quality_likert(df: pd.DataFrame) -> pd.DataFrame:
    difficulty_map = {
        "非常简单": 1,
        "较为简单": 2,
        "相对简单": 2,
        "适中": 3,
        "有一定挑战": 4,
        "非常有挑战": 5,
    }
    time_map = {
        "非常紧张": 1,
        "较为紧张": 2,
        "适中": 3,
        "较为充足": 4,
        "非常充足": 5,
    }
    review_map = {
        "基本没有帮助": 1,
        "帮助较少": 2,
        "适中": 3,
        "比较有帮助": 4,
        "非常有帮助": 5,
    }
    ease_map = {
        "非常简单": 5,
        "相对简单": 4,
        "一般": 3,
        "较为复杂": 2,
        "非常复杂": 1,
        "我无法使用对话助手": 0,
    }

    mappings = {
        "对测试质量的评价_0": difficulty_map,
        "对测试质量的评价_1": difficulty_map,
        "对测试质量的评价_2": time_map,
        "对测试质量的评价_3": time_map,
        "对测试质量的评价_4": time_map,
        "对测试质量的评价_5": review_map,
        "对测试质量的评价_7": ease_map,
    }

    for col, mapping in mappings.items():
        if col in df.columns:
            df[col] = df[col].map(mapping)

    rename_map = {
        "对测试质量的评价_0": "HW1 Difficulty",
        "对测试质量的评价_1": "HW2 Difficulty",
        "对测试质量的评价_2": "HW1 Time Sufficiency",
        "对测试质量的评价_3": "HW2 Time Sufficiency",
        "对测试质量的评价_4": "Learning Time Sufficiency",
        "对测试质量的评价_5": "Review Helpfulness",
        "对测试质量的评价_7": "Assistant Ease of Use",
    }
    return df.rename(columns=rename_map)
