description = """
## 检查正数
编写一个函数`is_positive(num)`，它接受一个整数，并检查该数是否为正数。如果是正数返回布尔值True，否则返回布尔值False。（1 分）
"""

title = "检查正数（1 分）"
score = 1

knowledge = ["condition", "bool"]

code_template = """
def is_positive(num):
    # 你的代码
    return ...
"""

code_entrypoint = "is_positive"

validcases = [
    {"input": [10], "output": True, "comment": "10是正数"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [1], "output": True, "comment": "1是正数"},
    {"input": [0], "output": False, "comment": "0不是正数"},
    {"input": [-1], "output": False, "comment": "-1不是正数"},
    {"input": [100], "output": True, "comment": "100是正数"},
    {"input": [-100], "output": False, "comment": "-100不是正数"},
]

answer = """
```Python
def is_positive(num):
    return num > 0
```
"""
