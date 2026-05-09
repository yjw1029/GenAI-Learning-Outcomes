description = """
## 寻找缺失的数字
给定一个包含从 0 到 n 的 n 个不同数字的列表，但缺少其中一个数字。编写一个函数`find_missing_number(nums)`，它返回缺失的数字。（4 分）
"""

title = "寻找缺失的数字（4 分）"
score = 4

knowledge = ["list", "number"]

code_template = """
def find_missing_number(nums):
    # 你的代码
    return ...
"""

code_entrypoint = "find_missing_number"

validcases = [
    {"input": [[0, 3, 7, 1, 2, 8, 4, 5]], "output": 6, "comment": "0到8之间缺失的数字是6"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [[0, 1, 2, 4, 5]], "output": 3, "comment": "0到5之间缺失的数字是3"},
    {"input": [[1, 2, 3, 4, 5]], "output": 0, "comment": "0到5之间缺失的数字是0"},
    {"input": [[0]], "output": 1, "comment": "0到1之间缺失的数字是1"},
    {
        "input": [[0, 1, 2, 3, 4, 5, 6, 7, 8]],
        "output": 9,
        "comment": "0到9之间缺失的数字是9",
    },
    {"input": [[5, 3, 1, 2, 4, 0, 7]], "output": 6, "comment": "0到7之间缺失的数字是6"},
]

answer = """
```Python
def find_missing_number(nums):
    n = len(nums)
    total = n * (n + 1) // 2
    actual_sum = sum(nums)
    return total - actual_sum
```
"""
