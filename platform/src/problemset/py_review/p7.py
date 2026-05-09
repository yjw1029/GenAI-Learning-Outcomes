description = """
## 判断整数正负
给定一个整数变量`x`，编写一个函数`judge_integer_sign`，根据`x`的值分别赋给变量`s`字符串"POSITIVE"、"NEGATIVE"或"ZERO"（分别对应`x`是正数、负数或零）。（2 分）
"""

title = "判断整数正负（2 分）"
score = 2

knowledge = ["number", "condition"]

code_template = """
def judge_integer_sign(x):
    # 你的代码
    return ...
"""

code_entrypoint = "judge_integer_sign"

validcases = [
    {"input": [5], "output": "POSITIVE", "comment": "5是正数，所以输出 'POSITIVE'"},
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [0],
        "output": "ZERO",
        "comment": "0既不是正数也不是负数，所以输出 'ZERO'",
    },
    {"input": [-1], "output": "NEGATIVE", "comment": "-1是负数，所以输出 'NEGATIVE'"},
    {"input": [10], "output": "POSITIVE", "comment": "10是正数，所以输出 'POSITIVE'"},
    {
        "input": [-100],
        "output": "NEGATIVE",
        "comment": "-100是负数，所以输出 'NEGATIVE'",
    },
    {"input": [999], "output": "POSITIVE", "comment": "999是正数，所以输出 'POSITIVE'"},
]

answer = """
```Python
def judge_integer_sign(x):
    if x > 0:
        return "POSITIVE"
    elif x < 0:
        return "NEGATIVE"
    else:
        return "ZERO"
```
"""
