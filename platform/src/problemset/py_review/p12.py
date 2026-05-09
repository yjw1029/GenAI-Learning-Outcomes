description = """
## 列表中正数计数
编写一个函数`count_positives(nums)`，它接受一个数字列表`nums`作为参数，并返回列表中正数的数量。（2 分）
"""

title = "列表中正数计数（2 分）"
score = 2

knowledge = ["list", "loop"]

code_template = """
def count_positives(nums):
    # 你的代码
    return ...
"""

code_entrypoint = "count_positives"

validcases = [
    {
        "input": [[1, -4, 0, 5, 3]],
        "output": 3,
        "comment": "列表中的正数有 1, 5, 3，总共 3 个",
    },
]

testcases = [
    *validcases,
    # common cases
    {"input": [[-1, -2, -3, -4]], "output": 0, "comment": "列表中没有正数"},
    {"input": [[0, 0, 0, 0]], "output": 0, "comment": "列表中没有正数，只有0"},
    {
        "input": [[5, 12, 2, 9]],
        "output": 4,
        "comment": "列表中的正数有 5, 12, 2, 9，总共 4 个",
    },
    {
        "input": [[-5, 3, -2, 1, 0]],
        "output": 2,
        "comment": "列表中的正数有 3, 1，总共 2 个",
    },
    {"input": [[1]], "output": 1, "comment": "列表中只有一个正数 1"},
    {"input": [[-1, 0, 1]], "output": 1, "comment": "列表中的正数有 1，总共 1 个"},
]

answer = """
```Python
def count_positives(nums):
    count = 0
    for num in nums:
        if num > 0:
            count += 1
    return count
```
"""
