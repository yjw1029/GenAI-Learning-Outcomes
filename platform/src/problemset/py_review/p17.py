description = """
## 移除列表元素
给你一个列表`nums`和一个值`val`，你需要移除所有数值等于`val`的元素，并返回移除后的数组。元素的顺序不能改变。（3 分）
"""

title = "移除列表元素（3 分）"
score = 3

knowledge = ["list", "condition", "loop"]

code_template = """
def remove_elements(nums, val):
    # 你的代码
    return ...
"""

code_entrypoint = "remove_elements"

validcases = [
    {"input": [[3, 2, 2, 3], 3], "output": [2, 2], "comment": "移除所有值为 3 的元素"},
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [[1, 2, 3, 4, 5], 3],
        "output": [1, 2, 4, 5],
        "comment": "移除一个中间值",
    },
    {"input": [[5, 5, 5, 5], 5], "output": [], "comment": "移除所有元素"},
    {"input": [[1, 2, 3], 4], "output": [1, 2, 3], "comment": "没有元素被移除"},
    {"input": [[], 1], "output": [], "comment": "空列表"},
    {"input": [[2, 3, 3, 2, 4], 3], "output": [2, 2, 4], "comment": "移除多个连续元素"},
    {"input": [[1, 2, 2, 1], 2], "output": [1, 1], "comment": "移除多个非连续元素"},
]

answer = """
```Python
def remove_elements(nums, val):
    i = 0
    for num in nums:
        if num != val:
            nums[i] = num
            i += 1
    return nums[:i]
```
"""
