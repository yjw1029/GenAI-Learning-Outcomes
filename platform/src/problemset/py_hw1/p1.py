description = """
## n次方
给定一个整数`x`（可以为0、正整数和负整数）和非负整数`n`，编写一个函数`power(x, n)`，它接受这两个整数作为参数，并返回`x`的`n`次方。（1 分）
"""

title = "n次方 (1分)"
score = 1

knowledge = ["number"]

code_template = """
def power(x, n):
    # 你的代码
    return ...
"""

code_entrypoint = "power"

validcases = [
    {"input": [2, 3], "output": 8, "comment": "2^3 = 8"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [3, 2], "output": 9, "comment": "3^2 = 9"},
    {"input": [10, 0], "output": 1, "comment": "10^0 = 1"},
    {"input": [1, 100], "output": 1, "comment": "1^100 = 1"},
    {"input": [0, 5], "output": 0, "comment": "0^5 = 0"},
    {"input": [-2, 4], "output": 16, "comment": "(-2)^4 = 16"},
    {"input": [-3, 3], "output": -27, "comment": "(-3)^3 = -27"},
]

answer = """
```Python
def power(x, n):
    return x ** n
```
"""
