description = """
## 计算平均分
编写一个函数 `calculate_average(scores)`，它接受一个分数列表 `scores`（由整数组成）作为参数，并返回列表中分数的平均值。（2 分）
"""

title = "计算平均分（2 分）"
score = 2

knowledge = ["list", "loop", "number"]

code_template = """
def calculate_average(scores):
    # 你的代码
    return ...
"""

code_entrypoint = "calculate_average"

validcases = [
    {
        "input": [[80, 90, 100]],
        "output": 90.0,
        "comment": "平均分是 (80 + 90 + 100) / 3 = 90.0",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [[50, 60, 70, 80]],
        "output": 65.0,
        "comment": "平均分是 (50 + 60 + 70 + 80) / 4 = 65.0",
    },
    {"input": [[100, 100, 100]], "output": 100.0, "comment": "全部分数都是 100"},
    {"input": [[40, 50]], "output": 45.0, "comment": "平均分是 (40 + 50) / 2 = 45.0"},
    {
        "input": [[77, 88, 99, 66, 55]],
        "output": 77.0,
        "comment": "平均分是 (77 + 88 + 99 + 66 + 55) / 5 = 77.0",
    },
    {"input": [[83]], "output": 83.0, "comment": "只有一个分数时，平均分即为该分数"},
]

answer = """
```Python
def calculate_average(scores):
    total = 0
    for score in scores:
        total += score
    return total / len(scores) if len(scores) > 0 else 0
```
"""
