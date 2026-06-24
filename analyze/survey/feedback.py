"""Participant-feedback survey loading, normalization, and summaries."""
from __future__ import annotations

import math
from typing import Iterable

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from analyze.config import (
    MATH_HW1_PROBLEMS,
    MATH_HW2_PROBLEMS,
    MATH_SCORE_FILE,
    MATH_SCORE_MAP,
    PRESURVEY_FILE,
    PYTHON_SCORE_FILE,
    VALIDUSER_FILE,
)
from analyze.config.paths import CAPTEST_SCORE_FILE
from analyze.core import (
    load_capability_scores,
    load_homework_scores,
    load_presurvey_data,
    load_valid_users,
    merge_presurvey_to_df,
    prepare_covariates,
)
from analyze.survey.participant_feedback import (
    REPO_ROOT,
    RISK_LABELS,
    RISK_OVERLAP_ITEMS,
    add_behavior_supergroup_math,
    add_behavior_supergroup_python,
    load_postsurvey_data,
    load_prepost_attitudes,
    map_likert_scale_values,
    map_multiselect_values,
    run_participant_feedback_analysis,
)


COURSE_ORDER = ["math", "python"]

INDICATOR_LABELS = {
    "survey_use_when_stuck": "Use when stuck",
    "survey_answer_checking": "Answer checking",
    "survey_concept_or_solution": "Concept/solution help",
    "survey_answer_seeking": "Answer seeking",
    "survey_throughout_learning": "Throughout learning",
    "survey_positive_integration": "Positive integration",
}

MULTISELECT_QUESTIONS = [
    (
        "目的_3",
        "Integration pattern",
        [
            "Use when stuck",
            "Throughout learning",
            "Early-stage only",
            "Late-stage review",
            "Rarely use",
            "Other",
        ],
    ),
]


def _contains_any(value: object, targets: Iterable[str]) -> bool:
    if value is None:
        return False
    target_set = set(targets)
    if isinstance(value, list):
        items = [str(v).strip() for v in value]
    elif isinstance(value, str):
        items = [v.strip() for v in value.split(";")]
    else:
        try:
            if pd.isna(value):
                return False
        except (TypeError, ValueError):
            pass
        items = [str(value).strip()]
    return any(item in target_set for item in items if item)


def _risk_contains(value: object, label_fragment: str) -> bool:
    if not isinstance(value, set):
        return False
    return any(label_fragment in str(item) for item in value)


def _wilson_ci(k: float, n: float, z: float = 1.96) -> tuple[float, float]:
    if n <= 0:
        return (math.nan, math.nan)
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = z / denom * math.sqrt((p * (1.0 - p) + z * z / (4.0 * n)) / n)
    return max(0.0, center - half), min(1.0, center + half)


def _mean_ci(values: pd.Series, z: float = 1.96) -> tuple[float, float, float]:
    clean = values.dropna().astype(float)
    if clean.empty:
        return (math.nan, math.nan, math.nan)
    mean = float(clean.mean())
    if len(clean) <= 1:
        return (mean, math.nan, math.nan)
    half = z * float(clean.std(ddof=1)) / math.sqrt(len(clean))
    return mean, mean - half, mean + half


def _selected(value: object, option: str) -> bool:
    return _contains_any(value, [option])


def _zscore_within_course(df: pd.DataFrame, column: str) -> pd.Series:
    def _z(s: pd.Series) -> pd.Series:
        sd = s.std(ddof=0)
        if not sd or pd.isna(sd):
            return pd.Series(0.0, index=s.index)
        return (s - s.mean()) / sd

    return df.groupby("course", group_keys=False)[column].transform(_z)


def _categorize_university(value: object) -> str | None:
    if pd.isna(value) or float(value) == 0:
        return None
    value_f = float(value)
    if value_f >= 4:
        return "High"
    if value_f >= 2:
        return "Mid"
    return "Low"


def _categorize_capability(score: object, course: str) -> str | None:
    if pd.isna(score):
        return None
    score_f = float(score)
    if course == "python":
        if score_f < 3:
            return "Low"
        if score_f <= 6.5:
            return "Mid"
        return "High"
    if score_f <= 3.5:
        return "Low"
    if score_f <= 6.5:
        return "Mid"
    return "High"


def build_feedback_mechanism_dataset() -> pd.DataFrame:
    """Return one row per valid user with survey, behavior, and attitude fields."""
    python_users, math_users = load_valid_users(VALIDUSER_FILE)
    py_captest, math_captest = load_capability_scores(CAPTEST_SCORE_FILE)
    py_scores, math_scores = load_homework_scores(
        PYTHON_SCORE_FILE,
        MATH_SCORE_FILE,
        MATH_HW1_PROBLEMS,
        MATH_HW2_PROBLEMS,
        MATH_SCORE_MAP,
    )
    presurvey = load_presurvey_data(PRESURVEY_FILE)

    python_df = (
        python_users.merge(py_captest, on="username", how="left")
        .merge(py_scores, on="username", how="left")
    )
    math_df = (
        math_users.merge(math_captest, on="username", how="left")
        .merge(math_scores, on="username", how="left")
    )
    python_df = prepare_covariates(merge_presurvey_to_df(python_df, presurvey, "python"), "python")
    math_df = prepare_covariates(merge_presurvey_to_df(math_df, presurvey, "math"), "math")

    python_df = add_behavior_supergroup_python(python_df)
    math_df = add_behavior_supergroup_math(math_df)
    users = pd.concat([python_df, math_df], ignore_index=True)

    post = map_multiselect_values(load_postsurvey_data())
    post = post.drop(columns=[c for c in ("group", "course") if c in post.columns])
    attitudes = load_prepost_attitudes().drop(columns=["group", "course"])

    df = users.merge(post, on="username", how="left").merge(attitudes, on="username", how="left")
    df["behavior_supergroup"] = df["behavior_supergroup"].where(df["group"] == 1)
    df["behavior_supergroup"] = df["behavior_supergroup"].fillna("passive")
    df["feedback_group"] = np.where(df["group"] == 0, "control", df["behavior_supergroup"])
    df["observed_proactive"] = (
        (df["group"] == 1) & (df["behavior_supergroup"] == "proactive_critical")
    ).astype(int)
    df["observed_passive"] = (
        (df["group"] == 1) & (df["behavior_supergroup"] == "passive")
    ).astype(int)

    df["survey_use_when_stuck"] = df["目的_3"].apply(lambda x: _contains_any(x, ["Use when stuck"]))
    df["survey_throughout_learning"] = df["目的_3"].apply(
        lambda x: _contains_any(x, ["Throughout learning"])
    )
    df["survey_answer_checking"] = (
        df["目的_1"].apply(lambda x: _contains_any(x, ["Answer checking"]))
        | df["目的_2"].apply(lambda x: _contains_any(x, ["Answer checking"]))
    )
    df["survey_concept_or_solution"] = (
        df["目的_1"].apply(
            lambda x: _contains_any(x, ["Concept explanations", "Solution approach"])
        )
        | df["目的_2"].apply(
            lambda x: _contains_any(x, ["Concept explanations", "Solution approach"])
        )
    )
    df["survey_answer_seeking"] = (
        df["目的_1"].apply(lambda x: _contains_any(x, ["Specific answers"]))
        | df["目的_2"].apply(lambda x: _contains_any(x, ["Problem answers"]))
    )
    df["survey_positive_integration"] = (
        df["survey_use_when_stuck"]
        | df["survey_answer_checking"]
        | df["survey_concept_or_solution"]
    )

    for col in INDICATOR_LABELS:
        df[col] = df[col].astype(int)

    df["willingness_delta"] = df["post_willingness"] - df["pre_willingness"]
    df["post_overreliance_risk"] = df["post_risks"].apply(
        lambda x: _risk_contains(x, "过度依赖")
    ).astype(int)
    df["post_inaccuracy_risk"] = df["post_risks"].apply(
        lambda x: _risk_contains(x, "准确或可靠")
    ).astype(int)
    df["university_cat"] = df["university_ranking_num"].apply(_categorize_university)
    df["capability_cat"] = df.apply(
        lambda row: _categorize_capability(row["captest_score"], str(row["course"])),
        axis=1,
    )
    df["hw2_z"] = _zscore_within_course(df, "hw2_score")
    return df


def summarize_indicator_rates(
    df: pd.DataFrame,
    *,
    group_cols: list[str],
    indicators: list[str],
) -> pd.DataFrame:
    rows = []
    for keys, sub in df.groupby(group_cols, dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        base = dict(zip(group_cols, keys))
        n = len(sub)
        for indicator in indicators:
            k = float(sub[indicator].sum())
            lo, hi = _wilson_ci(k, n)
            rows.append(
                {
                    **base,
                    "indicator": indicator,
                    "label": INDICATOR_LABELS.get(indicator, indicator),
                    "n": n,
                    "count": int(k),
                    "rate": k / n if n else math.nan,
                    "ci95_low": lo,
                    "ci95_high": hi,
                }
            )
    return pd.DataFrame(rows)


def summarize_willingness(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (course, behavior), sub in df.groupby(["course", "feedback_group"]):
        mean, lo, hi = _mean_ci(sub["willingness_delta"])
        rows.append(
            {
                "course": course,
                "feedback_group": behavior,
                "n": int(sub["willingness_delta"].notna().sum()),
                "mean": mean,
                "ci95_low": lo,
                "ci95_high": hi,
            }
        )
    return pd.DataFrame(rows)


def summarize_attitude_deltas(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    specs = [("willingness", "Willingness", "willingness_delta")]
    for item in RISK_OVERLAP_ITEMS:
        label = RISK_LABELS.get(item, item).replace("\n", " ")
        col = f"risk_delta_{label.lower().replace(' ', '_')}"
        has_prepost = df["post_risks"].apply(lambda s: isinstance(s, set)) & df[
            "pre_risks"
        ].apply(lambda s: isinstance(s, set))
        df[col] = np.where(
            has_prepost,
            df["post_risks"].apply(lambda s: item in s if isinstance(s, set) else False).astype(int)
            - df["pre_risks"].apply(lambda s: item in s if isinstance(s, set) else False).astype(int),
            np.nan,
        )
        specs.append((col, label, col))

    for (course, behavior), sub in df.groupby(["course", "feedback_group"]):
        for metric, label, col in specs:
            mean, lo90, hi90 = _mean_ci(sub[col], z=1.645)
            _mean, lo95, hi95 = _mean_ci(sub[col], z=1.96)
            rows.append(
                {
                    "course": course,
                    "feedback_group": behavior,
                    "metric": metric,
                    "label": label,
                    "n": int(sub[col].notna().sum()),
                    "mean": mean,
                    "ci90_low": lo90,
                    "ci90_high": hi90,
                    "ci95_low": lo95,
                    "ci95_high": hi95,
                }
            )
    return pd.DataFrame(rows)


def summarize_multiselect_by_behavior(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column, question_label, options in MULTISELECT_QUESTIONS:
        if column not in df.columns:
            continue
        valid_df = df[df[column].notna()].copy()
        for (course, behavior), sub in valid_df.groupby(["course", "feedback_group"]):
            if behavior == "control":
                continue
            n = len(sub)
            for option in options:
                k = float(sub[column].apply(lambda value: _selected(value, option)).sum())
                if k == 0 and option == "Other":
                    continue
                lo, hi = _wilson_ci(k, n)
                rows.append(
                    {
                        "course": course,
                        "feedback_group": behavior,
                        "question": column,
                        "question_label": question_label,
                        "response": option,
                        "n": n,
                        "count": int(k),
                        "rate": k / n if n else math.nan,
                        "ci95_low": lo,
                        "ci95_high": hi,
                    }
                )
    return pd.DataFrame(rows)


def fit_exam_score_models(df: pd.DataFrame) -> pd.DataFrame:
    """Fit compact OLS checks for whether self reports add to observed behavior."""
    model_df = df[
        [
            "hw2_z",
            "course",
            "observed_proactive",
            "survey_positive_integration",
            "survey_answer_seeking",
            "survey_throughout_learning",
            "captest_score",
            "university_ranking_num",
            "gpt_familiarity_num",
        ]
    ].dropna()
    formulas = {
        "behavior_only": "hw2_z ~ observed_proactive + captest_score + university_ranking_num + C(course)",
        "survey_only": (
            "hw2_z ~ survey_positive_integration + survey_answer_seeking "
            "+ survey_throughout_learning + captest_score + university_ranking_num + C(course)"
        ),
        "behavior_plus_survey": (
            "hw2_z ~ observed_proactive + survey_positive_integration + survey_answer_seeking "
            "+ survey_throughout_learning + captest_score + university_ranking_num + "
            "gpt_familiarity_num + C(course)"
        ),
    }
    rows = []
    for model_name, formula in formulas.items():
        result = smf.ols(formula, data=model_df).fit(cov_type="HC3")
        for term in result.params.index:
            rows.append(
                {
                    "model": model_name,
                    "term": term,
                    "coef": result.params[term],
                    "std_err": result.bse[term],
                    "p_value": result.pvalues[term],
                    "n": int(result.nobs),
                    "r2": result.rsquared,
                }
            )
    return pd.DataFrame(rows)
