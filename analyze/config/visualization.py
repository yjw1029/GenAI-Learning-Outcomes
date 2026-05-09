"""
Visualization configurations for plots and figures.

Defines color schemes, fonts, and display settings.
"""

# Visualization settings
NATURE_COLORS = ['#3C5488', '#EE8677']  # Deep blue and coral
CONTROL_COLOR = '#3C5488'
EXPERIMENT_COLOR = '#E64B35'
DIFF_COLOR = '#6A51A3'

# Likert scale colors (5-point scale from negative to positive)
# Red (Very Poor) -> Orange (Poor) -> Yellow (Neutral) -> Light Blue (Good) -> Dark Blue (Excellent)
LIKERT_5_COLORS = ['#d73027', '#fc8d59', '#fee090', '#91bfdb', '#4575b4']

# Font settings for plots
PLOT_FONT_SETTINGS = {
    'font.family': 'Arial',
    'font.sans-serif': 'Arial',
}

# Course group mappings
COURSE_GROUPS = {
    'py': 'Python',
    'pygpt': 'Python',
    'math': 'Game Theory',
    'mathgpt': 'Game Theory'
}

GROUP_LABEL_MAP = {
    'py': 'Control',
    'pygpt': 'Experiment',
    'math': 'Control',
    'mathgpt': 'Experiment'
}
