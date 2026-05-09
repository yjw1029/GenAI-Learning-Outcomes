description = """
## 回文数
设计一个函数`is_palindrome(x)`，给你一个整数`x`，如果`x`是一个回文整数，返回`True`；否则，返回`False`。（3 分）

提示: 使用`str`函数将整数转变为字符串。例如 `str(12345) = "12345"`
"""

title = "回文数 (3分)"
score = 3

knowledge = ["string", "condition"]

code_template = """
def is_palindrome(x):
    # 你的代码
    return ...
"""

code_entrypoint = "is_palindrome"

validcases = [
    {"input": [121], "output": True, "comment": "121是一个回文数"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [123], "output": False, "comment": "123不是一个回文数"},
    {"input": [-121], "output": False, "comment": "-121不是一个回文数，因为负号"},
    {"input": [10], "output": False, "comment": "10不是一个回文数"},
    {"input": [1], "output": True, "comment": "1是一个回文数"},
    {"input": [1221], "output": True, "comment": "1221是一个回文数"},
    {"input": [0], "output": True, "comment": "0是一个回文数"},
]
answer = ""
