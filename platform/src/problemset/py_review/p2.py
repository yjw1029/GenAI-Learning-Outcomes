description = """
## 列表取反
给定一个整数列表`lst`，创建一个新列表，其中包含原列表中每个值的相反数。例如，给定列表`[-1, 2, -3, 4]`，结果应为新列表`[1, -2, 3, -4]`。（1 分）
"""

title = "列表取反（1 分）"
score = 1

knowledge = ["list", "loop"]

code_template = """
def negate_list(lst):
    # 你的代码
    return ...
"""

code_entrypoint = "negate_list"

validcases = [
    {
        "input": [[-1, 2, -3, 4]],
        "output": [1, -2, 3, -4],
        "comment": "列表中每个元素的相反数",
    },
]

testcases = [
    *validcases,
    # common cases
    {"input": [[0, 0, 0]], "output": [0, 0, 0], "comment": "全零列表的相反数仍为全零"},
    {
        "input": [[-5, -4, -3, -2, -1]],
        "output": [5, 4, 3, 2, 1],
        "comment": "负数列表的相反数为正数",
    },
    {
        "input": [[1, 2, 3, 4, 5]],
        "output": [-1, -2, -3, -4, -5],
        "comment": "正数列表的相反数为负数",
    },
    {
        "input": [[-1, 0, 1]],
        "output": [1, 0, -1],
        "comment": "包含负数、零和正数的列表",
    },
    {"input": [[100]], "output": [-100], "comment": "单个正数的相反数"},
    {"input": [[-100]], "output": [100], "comment": "单个负数的相反数"},
]


answer = """
```Python
def negate_list(lst):
    negated_list = []
    for x in lst:
        negated_list.append(-x)
    return negated_list
```
"""
