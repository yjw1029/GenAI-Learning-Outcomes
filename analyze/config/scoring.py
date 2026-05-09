"""
Scoring configurations for homework and capability tests.

Defines score maps, correct answers, and problem lists.
"""

# Math score map (from ana.ipynb cell 11)
MATH_SCORE_MAP = {
    "math_hw1/p1": {
        "填空1": 0.25,
        "填空2": 0.25,
        "填空3": 0.25,
        "填空4": 0.25,
        "A1": 0.125,
        "A2": 0.125,
        "B1": 0.125,
        "B2": 0.125,
        "C1": 0.125,
        "C2": 0.125,
        "D1": 0.125,
        "D2": 0.125,
        "填空5": 1
    },
    "math_hw1/p2": {
        "A1": 0.125,
        "A2": 0.125,
        "B1": 0.125,
        "B2": 0.125,
        "C1": 0.125,
        "C2": 0.125,
        "D1": 0.125,
        "D2": 0.125,
        "填空1": 1.5,
        "填空2": 1.5,
    },
    "math_hw1/p3": {
        "填空1": 1,
        "填空2": 1,
        "填空3": 2,
        "填空4": 1,
    },
    "math_hw1/p4": {
        "填空1": 3,
        "填空2": 2,
        "填空3": 2,
    },
    "math_hw2/p1": {
        "填空1": 1.5,
        "填空2": 1.5
    },
    "math_hw2/p2": {
        "填空1": 0.25,
        "填空2": 0.25,
        "填空3": 0.25,
        "填空4": 0.25,
        "A1": 0.1875,
        "A2": 0.1875,
        "B1": 0.1875,
        "B2": 0.1875,
        "C1": 0.1875,
        "C2": 0.1875,
        "D1": 0.1875,
        "D2": 0.1875,
        "填空5": 1.5
    },
    "math_hw2/p3": {
        "填空1": 2,
        "填空2": 3,
    },
    "math_hw2/p4": {
        "填空1": 3,
        "填空2": 2,
        "填空3": 2,
        "填空4": 2,
        "填空5": 2,
    }
}

# Python capability test correct answers (verified against surveyset/captest_py.py)
PY_CAPTEST_ANSWERS = {
    "代码基础能力测试_0": "重复执行相同的代码",
    "代码基础能力测试_1": "重复利用代码，避免重复编写相同的代码",
    "代码基础能力测试_2": "程序中定义的π值（如 3.14159）",
    "代码基础能力测试_3": "存储100个用户的姓名",
    "代码基础能力测试_4": "是否为质数",
    "代码基础能力测试_5": "B",
    "代码基础能力测试_6": "A",
    "代码基础能力测试_7": "C",  # Fixed: was "D", correct answer is C (Fibonacci sum)
    "代码基础能力测试_8": "如果array为空，则访问array[LENGTH(array) - 1]将引发错误",  # Fixed: was list with wrong answer
    "代码基础能力测试_9": "找出数组中的最大值"
}

# Python capability test question weights (total = 10 points)
# Design principle: difficulty increases with question number
PY_CAPTEST_WEIGHTS = {
    "代码基础能力测试_0": 0.5,   # 基础概念：循环作用（最简单）
    "代码基础能力测试_1": 0.5,   # 基础概念：函数目的
    "代码基础能力测试_2": 0.5,   # 基础概念：常量定义
    "代码基础能力测试_3": 0.5,   # 基础概念：数组应用
    "代码基础能力测试_4": 1.0,   # 算法理解：质数判断逻辑
    "代码基础能力测试_5": 1.0,   # 算法理解：绝对值计算
    "代码基础能力测试_6": 1.5,   # 算法实现：整数反转（循环+取模）
    "代码基础能力测试_7": 1.5,   # 算法实现：斐波那契求和
    "代码基础能力测试_8": 1.5,   # 代码调试：边界条件错误
    "代码基础能力测试_9": 1.5,   # 算法理解：递归分治找最大值
}

# Python homework score map (from GPTMentor/gptmentor/problemset/py_hw1/*.py)
PY_SCORE_MAP = {
    "py_hw1/p1": 1,
    "py_hw1/p2": 2,
    "py_hw1/p3": 2,
    "py_hw1/p4": 3,
    "py_hw1/p5": 3,
    "py_hw1/p6": 4,
    "py_hw1/p7": 4,
    "py_hw1/p8": 5,
    "py_hw2/p1": 1,
    "py_hw2/p2": 2,
    "py_hw2/p3": 2,
    "py_hw2/p4": 3,
    "py_hw2/p5": 3,
    "py_hw2/p6": 4,
    "py_hw2/p7": 4,
    "py_hw2/p8": 5,
}

# Math capability test correct answers (from ana.ipynb cell 35)
MATH_CAPTEST_ANSWERS = {
    "数学基础能力测试_0": "1",
    "数学基础能力测试_1": "3",  # Contains '3'
    "数学基础能力测试_2": "-12",
    "数学基础能力测试_3": "16",
    "数学基础能力测试_4": "9"
}

# Math capability test question weights (total = 10 points)
# Design principle: difficulty increases with question number
MATH_CAPTEST_WEIGHTS = {
    "数学基础能力测试_0": 1.5,   # 分段函数最大值（分析两段函数，相对简单）
    "数学基础能力测试_1": 1.5,   # 解二元一次方程组（基础代数）
    "数学基础能力测试_2": 2,   # 求导并计算特定点的值（基础微积分）
    "数学基础能力测试_3": 2,   # 三次函数在区间上的最大值（求导+极值+端点比较）
    "数学基础能力测试_4": 3,     # 线性规划求最大值（约束条件+可行域+目标函数，最难）
}

# Python problem names for HW1 and HW2
PY_HW1_PROBLEMS = [f"py_hw1/p{i}" for i in range(1, 9)]
PY_HW2_PROBLEMS = [f"py_hw2/p{i}" for i in range(1, 9)]
PY_REVIEW_PROBLEMS = [f"py_review/p{i}" for i in range(1, 33)]

# Math problem names for HW1 and HW2
MATH_HW1_PROBLEMS = [f"math_hw1/p{i}" for i in range(1, 5)]
MATH_HW2_PROBLEMS = [f"math_hw2/p{i}" for i in range(1, 5)]
MATH_REVIEW_PROBLEMS = [f"math_review/p{i}" for i in range(1, 11)]
