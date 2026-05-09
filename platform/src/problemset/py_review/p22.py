description = """
## 计算阶乘
编写一个函数`factorial(n)`，它接受一个整数作为参数，并返回该整数的阶乘。阶乘定义为一个数`n`的阶乘是所有小于或等于`n`的正整数的乘积。例如，5的阶乘是`5×4×3×2×1=120`。如果输入的整数是负数，函数应该返回`None`。（4 分）
"""

title = "计算阶乘（4 分）"
score = 4

knowledge = ["list", "loop", "condition"]

code_template = """
def factorial(n):
    # 你的代码
    return ...
"""

code_entrypoint = "factorial"

validcases = [
    {"input": [5], "output": 120, "comment": "5! = 120"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [0], "output": 1, "comment": "0! = 1"},
    {"input": [1], "output": 1, "comment": "1! = 1"},
    {"input": [3], "output": 6, "comment": "3! = 6"},
    {"input": [10], "output": 3628800, "comment": "10! = 3628800"},
]

answer = """
```Python
def factorial(n):
    if n < 0:
        return None
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result
```
"""
