"""
Shared data processing utilities for educational data analysis.

This module provides reusable functions for loading, merging, and encoding
survey data, homework scores, and capability test scores.
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional

from analyze.utils.math_scoring import load_math_hw_scores
from analyze.utils.user_exclusion import load_excluded_usernames

from analyze.config.encoding import (
    COMMON_DEMOGRAPHIC_FIELDS,
    COMMON_GPT_FIELDS,
    PYTHON_KNOWLEDGE_FIELDS,
    MATH_KNOWLEDGE_FIELDS,
    COMMON_ENCODINGS,
    PYTHON_SPECIFIC_ENCODINGS,
    MATH_SPECIFIC_ENCODINGS,
    VALIDUSER_ENCODINGS,
)


# ============================================================================
# Data Loading Functions
# ============================================================================

def load_presurvey_data(
    presurvey_file: Path, exclude_user_file: Optional[Path] = None
) -> Dict[str, Dict[str, Any]]:
    """Load and return presurvey data from JSON file.

    Args:
        presurvey_file: Path to presurvey JSON file
        exclude_user_file: Optional path to excluded-user CSV (defaults to config)

    Returns:
        Dictionary mapping username to survey responses
    """
    print("\nLoading presurvey data...")
    with open(presurvey_file, 'r', encoding='utf-8') as f:
        presurvey = json.load(f)
    excluded = load_excluded_usernames(exclude_user_file)
    if excluded:
        presurvey = {u: v for u, v in presurvey.items() if u not in excluded}
    print(f"  Loaded presurvey data for {len(presurvey)} users")
    return presurvey


def load_valid_users(validuser_file: Path, exclude_user_file: Optional[Path] = None):
    """Load valid users and separate into Python and Math DataFrames.

    Extracts course type and experimental group from the course column:
    - 'pygpt' or 'mathgpt' → experimental group (group=1)
    - 'py' or 'math' → control group (group=0)

    Args:
        validuser_file: Path to valid users CSV file
        exclude_user_file: Optional path to excluded-user CSV (defaults to config)

    Returns:
        Tuple of (python_df, math_df)
    """
    print("\nLoading valid users...")
    valid_users_df = pd.read_csv(validuser_file)

    # Rename columns to English
    valid_users_df = valid_users_df.rename(columns={
        '账号': 'username',
        '课程': 'course_raw',
        '学校排名': 'university_ranking',
        '是否支付激励': 'paid_incentive',
        '机构': 'organization'
    })

    valid_users_df['username'] = valid_users_df['username'].str.strip()

    excluded = load_excluded_usernames(exclude_user_file)
    if excluded:
        valid_users_df = valid_users_df[~valid_users_df['username'].isin(excluded)].copy()

    # Extract group from course_raw column
    # If course contains 'gpt', it's experimental group (1), otherwise control (0)
    valid_users_df['group'] = valid_users_df['course_raw'].str.contains('gpt', case=False).astype(int)

    # Separate into Python and Math DataFrames
    python_df = valid_users_df[valid_users_df['course_raw'].str.contains('py', case=False)].copy()
    math_df = valid_users_df[valid_users_df['course_raw'].str.contains('math', case=False)].copy()

    # Normalize course names
    python_df['course'] = 'python'
    math_df['course'] = 'math'

    print(f"  Loaded {len(python_df)} Python users and {len(math_df)} Math users")
    print(f"    Python - Treatment: {(python_df['group']==1).sum()}, Control: {(python_df['group']==0).sum()}")
    print(f"    Math - Treatment: {(math_df['group']==1).sum()}, Control: {(math_df['group']==0).sum()}")

    return python_df, math_df


def load_capability_scores(captest_file: Path, exclude_user_file: Optional[Path] = None):
    """Load capability test scores and separate by course.

    Args:
        captest_file: Path to capability test scores JSON file
        exclude_user_file: Optional path to excluded-user CSV (defaults to config)

    Returns:
        Tuple of (py_captest_df, math_captest_df)
    """
    print("\nLoading capability scores...")

    with open(captest_file, 'r', encoding='utf-8') as f:
        captest_data = json.load(f)
    excluded = load_excluded_usernames(exclude_user_file)

    # Separate Python and Math scores
    py_records = []
    math_records = []

    for username, data in captest_data.items():
        if username in excluded:
            continue
        course = data.get('course', '')
        record = {
            'username': username,
            'captest_score': data.get('score', 0)
        }

        if 'py' in course.lower():
            py_records.append(record)
        elif 'math' in course.lower():
            math_records.append(record)

    py_captest = pd.DataFrame(py_records)
    math_captest = pd.DataFrame(math_records)

    print(f"  Loaded captest for {len(py_captest)} Python users and {len(math_captest)} Math users")
    return py_captest, math_captest


def load_homework_scores(py_scores_file: Path, math_scores_file: Path,
                        math_hw1_problems: List[str], math_hw2_problems: List[str],
                        math_score_map: Dict[str, Dict[str, float]],
                        exclude_user_file: Optional[Path] = None):
    """Load homework scores and separate by course.

    Args:
        py_scores_file: Path to Python scores JSON file
        math_scores_file: Path to Math scores JSON file
        math_hw1_problems: List of problem IDs for Math HW1
        math_hw2_problems: List of problem IDs for Math HW2
        math_score_map: Mapping of problem fields to point values
        exclude_user_file: Optional path to excluded-user CSV (defaults to config)

    Returns:
        Tuple of (py_scores_df, math_scores_df)
    """
    print("\nLoading homework scores...")

    excluded = load_excluded_usernames(exclude_user_file)

    # Load Python scores from JSON
    with open(py_scores_file, 'r', encoding='utf-8') as f:
        py_data = json.load(f)

    py_records = []
    for username, scores in py_data.items():
        if username in excluded:
            continue
        py_records.append({
            'username': username,
            'hw1_score': scores.get('HW1', 0),
            'hw2_score': scores.get('HW2', 0)
        })
    py_scores = pd.DataFrame(py_records)

    # Load math scores (supports both old and new review-file schemas):
    # - old: data[user][problem] = {"填空1": 1, ...}
    # - new: data[user][problem] = {"scores": {...}, "user_answer": ..., "answer_id": ...}
    math_scores_dict = load_math_hw_scores(
        Path(math_scores_file),
        hw1_problems=list(math_hw1_problems),
        hw2_problems=list(math_hw2_problems),
        score_map=dict(math_score_map),
    )
    if excluded:
        math_scores_dict = {u: v for u, v in math_scores_dict.items() if u not in excluded}
    math_records = [{"username": u, **row} for u, row in math_scores_dict.items()]
    math_scores = pd.DataFrame(math_records)

    print(f"  Loaded homework scores for {len(py_scores)} Python users and {len(math_scores)} Math users")
    return py_scores, math_scores


# ============================================================================
# Data Merging Functions
# ============================================================================

def merge_presurvey_to_df(df: pd.DataFrame, presurvey: Dict[str, Dict[str, Any]],
                         course_type: str) -> pd.DataFrame:
    """Merge presurvey data into the course DataFrame.

    Args:
        df: DataFrame with user data
        presurvey: Dictionary of presurvey responses
        course_type: 'python' or 'math'

    Returns:
        DataFrame with merged presurvey fields
    """
    print(f"\nMerging presurvey data for {course_type}...")

    # Merge common demographic fields
    for presurvey_field, column_name in COMMON_DEMOGRAPHIC_FIELDS.items():
        df[column_name] = df['username'].map(lambda u: presurvey.get(u, {}).get(presurvey_field))

    # Merge common GPT fields
    for presurvey_field, column_name in COMMON_GPT_FIELDS.items():
        df[column_name] = df['username'].map(lambda u: presurvey.get(u, {}).get(presurvey_field))

    # Merge course-specific knowledge fields
    if course_type == 'python':
        for presurvey_field, column_name in PYTHON_KNOWLEDGE_FIELDS.items():
            df[column_name] = df['username'].map(lambda u: presurvey.get(u, {}).get(presurvey_field))
    elif course_type == 'math':
        for presurvey_field, column_name in MATH_KNOWLEDGE_FIELDS.items():
            df[column_name] = df['username'].map(lambda u: presurvey.get(u, {}).get(presurvey_field))
    else:
        raise ValueError(f"Unknown course_type: {course_type}")

    print(f"  Merged presurvey data for {len(df)} {course_type} users")
    return df


# ============================================================================
# Encoding Functions
# ============================================================================

def encode_field(series: pd.Series, encoding_map: Dict[str, Any],
                field_name: str) -> pd.Series:
    """Encode a pandas Series using the provided mapping.

    Args:
        series: Series to encode
        encoding_map: Dictionary mapping values to numeric codes
        field_name: Name of the field (for error reporting)

    Returns:
        Encoded Series with numeric values
    """
    # Use .map() which handles NaN/None gracefully
    encoded = series.map(encoding_map)

    # Fill unmapped values with 0 (default for unknown/missing)
    encoded = encoded.fillna(0)

    return encoded


def apply_encodings(df: pd.DataFrame, encoding_specs: Dict[str, Dict[str, Any]],
                   suffix: str = '_num') -> pd.DataFrame:
    """Apply multiple encodings to a DataFrame.

    Args:
        df: DataFrame to encode
        encoding_specs: Dictionary mapping column names to encoding maps
        suffix: Suffix to add to encoded column names (default: '_num')

    Returns:
        DataFrame with new encoded columns added
    """
    for column_name, encoding_map in encoding_specs.items():
        if column_name in df.columns:
            encoded_column = f"{column_name}{suffix}"
            df[encoded_column] = encode_field(df[column_name], encoding_map, column_name)
        else:
            # Create zero-filled column if source column doesn't exist
            df[f"{column_name}{suffix}"] = 0

    return df


def prepare_covariates(df: pd.DataFrame, course_type: str) -> pd.DataFrame:
    """Prepare covariate matrix for IPW calculation.

    Applies all necessary encodings for the specified course type.

    Args:
        df: DataFrame with raw survey data
        course_type: 'python' or 'math'

    Returns:
        DataFrame with encoded covariate columns
    """
    print(f"\nPreparing covariates for {course_type}...")

    # Create a copy to avoid modifying original
    df_copy = df.copy()

    # Group indicator should already be present from load_valid_users()
    if 'group' not in df_copy.columns:
        raise ValueError("Group column not found in DataFrame. Ensure load_valid_users() is called first.")

    # Apply encoding from valid_users file (university_ranking)
    df_copy = apply_encodings(df_copy, VALIDUSER_ENCODINGS)

    # Apply major classification and encoding
    # Import here to avoid circular dependency
    from analyze.config.major_classification import classify_major, get_major_encoding

    # Classify majors into categories
    df_copy['major_category'] = df_copy['major'].apply(classify_major)

    # Encode major categories based on course type
    major_encoding_map = get_major_encoding(course_type)
    df_copy['major_num'] = df_copy['major_category'].map(major_encoding_map).fillna(0)

    print(f"  Major classification: {df_copy['major_category'].value_counts().to_dict()}")

    # Apply common encodings
    df_copy = apply_encodings(df_copy, COMMON_ENCODINGS)

    # Apply course-specific encodings
    if course_type == 'python':
        df_copy = apply_encodings(df_copy, PYTHON_SPECIFIC_ENCODINGS)
    elif course_type == 'math':
        df_copy = apply_encodings(df_copy, MATH_SPECIFIC_ENCODINGS)
    else:
        raise ValueError(f"Unknown course_type: {course_type}")

    # Capability test score (already numeric, but fill NaN with 0)
    df_copy['captest_score'] = df_copy['captest_score'].fillna(0)

    print(f"  Prepared covariates for {len(df_copy)} {course_type} users")
    return df_copy

