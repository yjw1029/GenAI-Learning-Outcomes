description = """
## 大于特定值计数
编写一个函数`count_greater_than`，给定一个整数列表 `lst` 和一个整数变量 `val`，编写一个循环来计算列表中严格大于 `val` 的值的数量。（2 分）
"""

title = "大于特定值计数（2 分）"
score = 2

knowledge = ["list", "loop", "condition"]

code_template = """
def count_greater_than(lst, val):
    # 你的代码
    return ...
"""

code_entrypoint = "count_greater_than"

validcases = [
    {"input": [[-1, -2, -3, -4], 0], "output": 0, "comment": "列表中没有大于0的元素"},
    {
        "input": [[1, 2, 3, 4], 2],
        "output": 2,
        "comment": "列表中有2个元素（3和4）大于2",
    },
]

testcases = [
    *validcases,
    # common cases
    {"input": [[5, 6, 7, 8], 7], "output": 1, "comment": "列表中有1个元素（8）大于7"},
    {
        "input": [[10, 20, 30, 40], 25],
        "output": 2,
        "comment": "列表中有2个元素（30和40）大于25",
    },
    {"input": [[0, 0, 0, 0], 0], "output": 0, "comment": "列表中没有大于0的元素"},
    {
        "input": [[-5, -4, -3, -2, -1], -3],
        "output": 2,
        "comment": "列表中有2个元素（-2和-1）大于-3",
    },
    {"input": [[1, 1, 1, 1], 1], "output": 0, "comment": "列表中没有大于1的元素"},
    {"input": [[], 5], "output": 0, "comment": "空列表中没有元素大于5"},
]

answer = """
```Python
def count_greater_than(lst, val):
    count = 0
    for num in lst:
        if num > val:
            count += 1
    return count
```
"""
