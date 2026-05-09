title = "数学基础能力测试"
description = """请同学在5分钟内完成以下的数学能力测试题"""

questions = {
    "数学基础能力测试": [
        {
            "text": r"""分段函数极值：考虑分段函数f(x)，找到该分段函数在其定义域内的最大值。

$$
f(x) = \\begin{cases}
    2x - 1    & \\text{当 } -2 \\leq x \\leq 1, \\\\
    -x^2      & \\text{当 } x > 1
\\end{cases}
$$
""",
            "type": "textarea"
        },
        {
            "text": r"""解方程：考虑如下方程，求x的值。
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
            "text": r"求导：函数 \\(f(x) = 3x^4 - 8x^3 + 6x^2 - 12x + 2\\) 的导数 \\(f'(x)\\) 在 \\(x = 1\\) 处的值",
            "type": "single_choice",
            "options": [
                "2",
                "-12",
                "12",
                "0"
            ]
        },
        {
            "text": r"""函数极值：考虑函数\\(f(x) = x^3 - 6x^2 + 9x + 12\\)，找到函数\\(f(x)\\)在\\([-4, 4]\\)上的最大值。""",
            "type": "textarea"
        },
        {
            "text": r"""二元一次函数极值：最大化: \\(z = 2x + y\\)
约束条件：
\\begin{cases}
3x + y ≤ 12 \\\\
x + y ≤ 6 \\\\
x ≥ 0, y ≥ 0 
\\end{cases}

请找到\\(z\\)的最大值""",
            "type": "textarea"
        }
    ]
}

