"""
Path configurations for EduAnalyze project.

Defines all input/output paths used across the analysis pipeline.
"""

from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Input paths
VALIDUSER_FILE = PROJECT_ROOT / "data/processed/validuser_merged.csv"
EXCLUDE_USER_FILE = PROJECT_ROOT / "data/processed/exclude_user.csv"
PRESURVEY_FILE = PROJECT_ROOT / "data/processed/survey/presurvey_merged.json"
CAPTEST_FILE = PROJECT_ROOT / "data/processed/survey/captest_merged.json"
POSTSURVEY_FILE = PROJECT_ROOT / "data/processed/survey/postsurvey_merged.json"
BEHAVIORS_DB = PROJECT_ROOT / "data/processed/behaviors/merged_behaviors.db"
CAPTEST_SCORE_FILE = PROJECT_ROOT / "data/annotation/captest_scores.json"
# Reviewed per-blank correctness + extracted user answers (see `analyze/export_math_score_reviews_with_answers.py`).
MATH_SCORE_FILE = PROJECT_ROOT / "data/annotation/math_score_reviews_with_answers.json"
PYTHON_SCORE_FILE = PROJECT_ROOT / "data/annotation/python_scores.json"

# Output paths
SCORES_DIR = PROJECT_ROOT / "data/annotation"
FIGURES_DIR = PROJECT_ROOT / "figures"

# Ensure output directories exist
SCORES_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
