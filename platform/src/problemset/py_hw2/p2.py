description = """
## 绝对值
给定两个数值`x`和`y`，设计一个函数`absolute_difference(x, y)`，计算他们差的绝对值。（2分）
"""

title = "绝对值 (2分)"
score = 2

knowledge = ["number", "condition"]

code_template = """
def absolute_difference(x, y):
    # 你的代码
    return ...
"""

code_entrypoint = "absolute_difference"

validcases = [
    {"input": [3, 7], "output": 4, "comment": "绝对值差 |3 - 7| = 4"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [10, 5], "output": 5, "comment": "绝对值差 |10 - 5| = 5"},
    {"input": [-3, 2], "output": 5, "comment": "绝对值差 |-3 - 2| = 5"},
    {"input": [0, 0], "output": 0, "comment": "绝对值差 |0 - 0| = 0"},
    {"input": [-5, -10], "output": 5, "comment": "绝对值差 |-5 - (-10)| = 5"},
    {"input": [15, -5], "output": 20, "comment": "绝对值差 |15 - (-5)| = 20"},
]
answer = ""
