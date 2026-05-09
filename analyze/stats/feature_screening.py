"""Statistical feature screening for appendix learner-profile selection."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import KFold

from analyze.config import MATH_SCORE_FILE, PRESURVEY_FILE, PYTHON_SCORE_FILE, VALIDUSER_FILE
from analyze.config.paths import CAPTEST_SCORE_FILE
from analyze.config.scoring import MATH_HW1_PROBLEMS, MATH_HW2_PROBLEMS, MATH_SCORE_MAP
from analyze.core.data_processing import (
    load_capability_scores,
    load_homework_scores,
    load_presurvey_data,
    load_valid_users,
    merge_presurvey_to_df,
    prepare_covariates,
)

def build_background_features(course_type: str) -> pd.DataFrame:
    presurvey = load_presurvey_data(PRESURVEY_FILE)
    python_df, math_df = load_valid_users(VALIDUSER_FILE)
    py_captest, math_captest = load_capability_scores(CAPTEST_SCORE_FILE)
    py_homework, math_homework = load_homework_scores(
        py_scores_file=PYTHON_SCORE_FILE,
        math_scores_file=MATH_SCORE_FILE,
        math_hw1_problems=list(MATH_HW1_PROBLEMS),
        math_hw2_problems=list(MATH_HW2_PROBLEMS),
        math_score_map=dict(MATH_SCORE_MAP),
    )

    if course_type == "python":
        base_df = python_df.copy()
        captest_df = py_captest
        homework_df = py_homework
    elif course_type == "math":
        base_df = math_df.copy()
        captest_df = math_captest
        homework_df = math_homework
    else:
        raise ValueError(f"Unknown course_type: {course_type}")

    base_df = merge_presurvey_to_df(base_df, presurvey, course_type=course_type)
    base_df = base_df.merge(captest_df, on="username", how="left")
    base_df = base_df.merge(homework_df, on="username", how="left")
    base_df = prepare_covariates(base_df, course_type=course_type)

    base_df = base_df[base_df["hw2_score"] > 0].reset_index(drop=True)
    return base_df


def build_background_features_combined() -> pd.DataFrame:
    presurvey = load_presurvey_data(PRESURVEY_FILE)
    python_df, math_df = load_valid_users(VALIDUSER_FILE)
    py_captest, math_captest = load_capability_scores(CAPTEST_SCORE_FILE)
    py_homework, math_homework = load_homework_scores(
        py_scores_file=PYTHON_SCORE_FILE,
        math_scores_file=MATH_SCORE_FILE,
        math_hw1_problems=list(MATH_HW1_PROBLEMS),
        math_hw2_problems=list(MATH_HW2_PROBLEMS),
        math_score_map=dict(MATH_SCORE_MAP),
    )

    python_df = merge_presurvey_to_df(python_df, presurvey, course_type="python")
    math_df = merge_presurvey_to_df(math_df, presurvey, course_type="math")

    python_df = python_df.merge(py_captest, on="username", how="left")
    math_df = math_df.merge(math_captest, on="username", how="left")

    python_df = python_df.merge(py_homework, on="username", how="left")
    math_df = math_df.merge(math_homework, on="username", how="left")

    python_df = prepare_covariates(python_df, course_type="python")
    math_df = prepare_covariates(math_df, course_type="math")

    df = pd.concat([python_df, math_df], ignore_index=True)
    df = df[df["hw2_score"] > 0].reset_index(drop=True)
    return df


def normalize_university_ranking_from_num(value: float | int | None) -> str | None:
    if pd.isna(value) or value == 0:
        return None
    if value >= 4:
        return "High"
    if value >= 2:
        return "Mid"
    return "Low"


def categorize_capability_from_score(score: float | int | None, course_type: str) -> str | None:
    if pd.isna(score):
        return None
    if course_type == "python":
        if score < 3:
            return "Low"
        if score < 7:
            return "Mid"
        return "High"
    if score <= 3:
        return "Low"
    if score < 7:
        return "Mid"
    return "High"


def get_background_feature_cols(course_type: str) -> list[str]:
    common_cols = [
        "university_ranking_num",
        "major_num",
        "grade_num",
        "class_ranking_num",
        "first_gen_num",
        "economic_status_num",
        "gpt_usage_num",
        "gpt_frequency_num",
        "gpt_familiarity_num",
        "captest_score",
    ]
    if course_type in {"python", "math", "combined"}:
        return common_cols
    return common_cols


def get_feature_display_names() -> dict[str, str]:
    return {
        "university_ranking_num": "University Ranking",
        "major_num": "Major",
        "grade_num": "Year in Program",
        "class_ranking_num": "Class Rank",
        "first_gen_num": "First-Generation Status",
        "economic_status_num": "Socioeconomic Status",
        "gpt_usage_num": "LLM Usage",
        "gpt_frequency_num": "LLM Usage Frequency",
        "gpt_familiarity_num": "LLM Familiarity",
        "captest_score": "Prior Knowledge",
        "university_cat": "University Ranking",
        "capability_cat": "Prior Knowledge",
        "course": "Course",
    }


def _standardize_columns(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    df_std = df[cols].copy()
    for col in cols:
        mean = df_std[col].mean()
        std = df_std[col].std(ddof=0)
        if std == 0 or np.isnan(std):
            df_std[col] = 0.0
        else:
            df_std[col] = (df_std[col] - mean) / std
    return df_std


def run_feature_directional_coeffs(
    course_type: str,
) -> pd.DataFrame:
    if course_type == "combined":
        raise ValueError("Directional coefficients are defined for python or math only.")
    df = build_background_features(course_type)
    feature_cols = get_background_feature_cols(course_type)
    missing_cols = [c for c in feature_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing encoded columns for {course_type}: {missing_cols}")

    df = df.copy()
    df["university_cat"] = df["university_ranking_num"].apply(normalize_university_ranking_from_num)
    ordinal_map = {"Low": 1, "Mid": 2, "High": 3}
    df["university_cat_num"] = df["university_cat"].map(ordinal_map).fillna(0)
    df["capability_cat"] = df["captest_score"].apply(
        lambda x: categorize_capability_from_score(x, course_type)
    )
    df["capability_cat_num"] = df["capability_cat"].map(ordinal_map).fillna(0)

    feature_cols = [
        "university_cat_num" if c == "university_ranking_num" else
        "capability_cat_num" if c == "captest_score" else c
        for c in feature_cols
    ]

    X = _standardize_columns(df, feature_cols)
    y = df["hw2_score"].values

    try:
        import statsmodels.api as sm
    except ImportError as exc:
        raise ImportError(
            "statsmodels is required for p-values. "
            "Install with: ./.venv/bin/python -m pip install statsmodels"
        ) from exc

    X_df = pd.DataFrame(X, columns=feature_cols)
    n_samples, n_features = X_df.shape
    print(
        f"[{course_type}] Using univariate regressions for p-values "
        f"(n={n_samples}, k={n_features})."
    )
    records = []
    for col in feature_cols:
        series = X_df[col]
        if series.std(ddof=0) == 0:
            records.append(
                {
                    "feature": col,
                    "coef": 0.0,
                    "p_value": 1.0,
                    "ci_low": 0.0,
                    "ci_high": 0.0,
                }
            )
            continue
        X_one = sm.add_constant(series, has_constant="add")
        ols_one = sm.OLS(y, X_one).fit()
        coef = float(ols_one.params.iloc[1])
        p_value = float(ols_one.pvalues.iloc[1])
        ci_low, ci_high = ols_one.conf_int().iloc[1].tolist()
        records.append(
            {
                "feature": col,
                "coef": coef,
                "p_value": p_value,
                "ci_low": float(ci_low),
                "ci_high": float(ci_high),
            }
        )

    coef_df = pd.DataFrame(records)
    coef_df["feature"] = coef_df["feature"].replace(
        {"university_cat_num": "university_cat", "capability_cat_num": "capability_cat"}
    )
    coef_df["direction"] = coef_df["coef"].apply(
        lambda x: "positive" if x > 0 else "negative" if x < 0 else "zero"
    )
    display_map = get_feature_display_names()
    coef_df["feature_display"] = coef_df["feature"].map(display_map).fillna(coef_df["feature"])

    coef_df = coef_df.sort_values("coef", ascending=False).reset_index(drop=True)

    print(f"\n[{course_type}] Directional coefficients (standardized features):")
    print(coef_df[["feature_display", "coef", "p_value", "direction"]].to_string(index=False))

    return coef_df


def compute_feature_importance(
    course_type: str,
    random_state: int = 42,
    n_splits: int = 5,
    n_estimators: int = 300,
    max_depth: int | None = 6,
    min_samples_leaf: int = 5,
) -> pd.DataFrame:
    if course_type == "combined":
        df = build_background_features_combined()
    else:
        df = build_background_features(course_type)
    feature_cols = get_background_feature_cols(course_type)
    missing_cols = [c for c in feature_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing encoded columns for {course_type}: {missing_cols}")

    df = df.copy()
    df["university_cat"] = df["university_ranking_num"].apply(normalize_university_ranking_from_num)
    cap_course = "python" if course_type == "python" else "math"
    if course_type == "combined":
        df["capability_cat"] = df.apply(
            lambda row: categorize_capability_from_score(
                row["captest_score"],
                "python" if row["course"] == "python" else "math",
            ),
            axis=1,
        )
    else:
        df["capability_cat"] = df["captest_score"].apply(
            lambda x: categorize_capability_from_score(x, cap_course)
        )
    cat_order = ["Low", "Mid", "High"]
    df["university_cat"] = pd.Categorical(df["university_cat"], categories=cat_order, ordered=True)
    df["capability_cat"] = pd.Categorical(df["capability_cat"], categories=cat_order, ordered=True)
    # Treat all survey/background features as enums: one-hot and group SHAP per feature.
    feature_cols = [c for c in feature_cols if c not in {"university_ranking_num", "captest_score"}]
    dummy_frames: list[pd.DataFrame] = []
    feature_group_map: dict[str, str] = {}

    for col in feature_cols:
        dummies = pd.get_dummies(df[col], prefix=col, dtype=float, dummy_na=True)
        for dummy_col in dummies.columns:
            feature_group_map[dummy_col] = col
        dummy_frames.append(dummies)

    if course_type == "combined":
        course_dummies = pd.get_dummies(df["course"], prefix="course", dtype=float, dummy_na=True)
        for dummy_col in course_dummies.columns:
            feature_group_map[dummy_col] = "course"
        dummy_frames.append(course_dummies)

    uni_dummies = pd.get_dummies(
        df["university_cat"],
        prefix="university_cat",
        dtype=float,
        dummy_na=True,
    )
    for dummy_col in uni_dummies.columns:
        feature_group_map[dummy_col] = "university_cat"

    cap_dummies = pd.get_dummies(
        df["capability_cat"],
        prefix="capability_cat",
        dtype=float,
        dummy_na=True,
    )
    for dummy_col in cap_dummies.columns:
        feature_group_map[dummy_col] = "capability_cat"

    X_df = pd.concat(
        dummy_frames + [uni_dummies, cap_dummies],
        axis=1,
    )
    X = X_df.values
    if course_type == "combined":
        df["hw2_score_z"] = df.groupby("course")["hw2_score"].transform(
            lambda s: (s - s.mean()) / s.std(ddof=0) if s.std(ddof=0) else 0.0
        )
        y = df["hw2_score_z"].values
    else:
        y = df["hw2_score"].values

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    r2_scores: list[float] = []
    mae_scores: list[float] = []
    fold_importances: list[np.ndarray] = []

    for fold_idx, (train_idx, test_idx) in enumerate(kf.split(X), start=1):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        model = RandomForestRegressor(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1,
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        r2_scores.append(r2_score(y_test, y_pred))
        mae_scores.append(mean_absolute_error(y_test, y_pred))

        print(
            f"[{course_type}] fold {fold_idx}/{n_splits}: "
            f"R2={r2_scores[-1]:.3f}, MAE={mae_scores[-1]:.3f}"
        )

    model_full = RandomForestRegressor(
        n_estimators=n_estimators,
        random_state=random_state,
        n_jobs=-1,
        max_depth=max_depth,
        min_samples_leaf=min_samples_leaf,
    )
    model_full.fit(X, y)

    try:
        import shap
    except ImportError as exc:
        raise ImportError(
            "SHAP is required for appendix feature importance to match the "
            "original EduAnalyze analysis. Install shap/numba with a working "
            "LLVM toolchain before regenerating this figure."
        ) from exc

    explainer = shap.TreeExplainer(model_full)
    shap_values = explainer.shap_values(X)
    shap_importance = np.mean(np.abs(shap_values), axis=0)

    raw_importance_df = pd.DataFrame(
        {"feature": X_df.columns, "importance": shap_importance}
    )
    raw_importance_df["feature_group"] = raw_importance_df["feature"].map(
        lambda name: feature_group_map.get(name, name)
    )
    importance_df = (
        raw_importance_df.groupby("feature_group", as_index=False)["importance"].sum()
        .sort_values("importance", ascending=False)
        .rename(columns={"feature_group": "feature"})
    )
    if "course" in importance_df["feature"].values:
        importance_df = importance_df[importance_df["feature"] != "course"].reset_index(drop=True)

    print(
        f"[{course_type}] CV (n={len(df)}): "
        f"R2={np.mean(r2_scores):.3f}±{np.std(r2_scores):.3f}, "
        f"MAE={np.mean(mae_scores):.3f}±{np.std(mae_scores):.3f}"
    )
    print(f"[{course_type}] Features (reported): {feature_cols}")

    display_map = get_feature_display_names()
    importance_df = importance_df.copy()
    importance_df["feature_display"] = (
        importance_df["feature"].map(display_map).fillna(importance_df["feature"])
    )

    return importance_df
