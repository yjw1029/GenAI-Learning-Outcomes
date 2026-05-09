description = """
## 列表偶数和
编写一个函数 `sum_even(nums)`，它接受一个数字列表 `nums` 作为参数，并返回列表中所有偶数的和。（2 分）
"""

title = "列表偶数和（2 分）"
score = 2

knowledge = ["list", "loop"]

code_template = """
def sum_even(nums):
    # 你的代码
    return ...
"""

code_entrypoint = "sum_even"

validcases = [
    {"input": [[1, 2, 3, 4]], "output": 6, "comment": "列表中偶数的和为 2 + 4 = 6"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [[5, 7, 8]], "output": 8, "comment": "列表中偶数的和为 8"},
    {
        "input": [[10, 20, 30]],
        "output": 60,
        "comment": "列表中偶数的和为 10 + 20 + 30 = 60",
    },
    {"input": [[1, 3, 5]], "output": 0, "comment": "没有偶数，和为 0"},
    {
        "input": [[2, 4, 6, 8]],
        "output": 20,
        "comment": "列表中偶数的和为 2 + 4 + 6 + 8 = 20",
    },
    {
        "input": [[-2, -4, -6]],
        "output": -12,
        "comment": "负数偶数的和为 -2 + -4 + -6 = -12",
    },
    {"input": [[0, 1, 2]], "output": 2, "comment": "包含0和偶数2，和为 2"},
]

answer = """
```Python
def sum_even(nums):
    total = 0
    for num in nums:
        if num % 2 == 0:
            total += num
    return total
```
"""
