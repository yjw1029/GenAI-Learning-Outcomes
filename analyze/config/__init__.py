"""
Configuration package for EduAnalyze.

Exports only the configuration needed by the remaining analysis scripts.
"""

from .paths import (
    VALIDUSER_FILE,
    PRESURVEY_FILE,
    POSTSURVEY_FILE,
    PYTHON_SCORE_FILE,
    MATH_SCORE_FILE,
    FIGURES_DIR,
)

from .scoring import (
    MATH_SCORE_MAP,
    MATH_HW1_PROBLEMS,
    MATH_HW2_PROBLEMS,
)

from .visualization import (
    CONTROL_COLOR,
    EXPERIMENT_COLOR,
    DIFF_COLOR,
)

__all__ = [
    # Paths
    "VALIDUSER_FILE",
    "PRESURVEY_FILE",
    "POSTSURVEY_FILE",
    "PYTHON_SCORE_FILE",
    "MATH_SCORE_FILE",
    "FIGURES_DIR",
    # Scoring
    "MATH_SCORE_MAP",
    "MATH_HW1_PROBLEMS",
    "MATH_HW2_PROBLEMS",
    # Visualization
    "CONTROL_COLOR",
    "EXPERIMENT_COLOR",
    "DIFF_COLOR",
]
