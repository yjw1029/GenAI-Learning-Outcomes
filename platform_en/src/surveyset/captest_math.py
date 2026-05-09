title = "Math Basics Test"
description = """Please complete the following math basics test within 5 minutes."""

questions = {
    "Math Basics Test": [
        {
            "text": r"""Piecewise function extrema: For f(x), find the maximum value on its domain.

$$
f(x) = \\begin{cases}
    2x - 1    & \\text{when } -2 \\leq x \\leq 1, \\\\
    -x^2      & \\text{when } x > 1
\\end{cases}
$$
""",
            "type": "textarea"
        },
        {
            "text": r"""Solve the system: find x.
$$
\\begin{cases}
2x + 3y = 9 \\\\
4x - 2y = 10
\\end{cases}
$$
""",
            "type": "textarea"
        },
        {
            "text": r"Derivative: For \\(f(x) = 3x^4 - 8x^3 + 6x^2 - 12x + 2\\), find \\(f'(x)\\) at \\(x = 1\\)",
            "type": "single_choice",
            "options": [
                "2",
                "-12",
                "12",
                "0"
            ]
        },
        {
            "text": r"""Function maximum: For \\(f(x) = x^3 - 6x^2 + 9x + 12\\), find the maximum on \\([-4, 4]\\).""",
            "type": "textarea"
        },
        {
            "text": r"""Linear optimization: maximize \\(z = 2x + y\\)
Constraints:
\\begin{cases}
3x + y ≤ 12 \\\\
x + y ≤ 6 \\\\
x ≥ 0, y ≥ 0 
\\end{cases}

Find the maximum value of \\(z\\).""",
            "type": "textarea"
        }
    ]
}
