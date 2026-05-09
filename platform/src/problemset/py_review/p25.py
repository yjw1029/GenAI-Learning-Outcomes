description = """
## 查找多数元素
给定一个大小为 `n` 的数组，编写一个函数 `majority_element(nums)` 找到出现次数大于 `[n/2]` 的元素。如果没有任何元素出现次数超过 `[n/2]`，返回 `None`。（4 分）
"""

title = "查找多数元素（4 分）"
score = 4

knowledge = ["list", "loop", "condition"]

code_template = """
def majority_element(nums):
    # 你的代码
    return ...
"""

code_entrypoint = "majority_element"

validcases = [
    {"input": [[3, 2, 3]], "output": 3, "comment": "3 是出现次数超过一半的元素"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [[1, 1, 2, 2, 2]], "output": 2, "comment": "2 是出现次数超过一半的元素"},
    {
        "input": [[1, 2, 3, 4, 5]],
        "output": None,
        "comment": "没有任何元素出现次数超过一半",
    },
    {"input": [[6, 6, 6, 7, 7]], "output": 6, "comment": "6 是出现次数超过一半的元素"},
    {"input": [[8]], "output": 8, "comment": "只有一个元素时，默认为多数元素"},
    {
        "input": [[9, 9, 9, 10, 10, 10, 10]],
        "output": 10,
        "comment": "10 是出现次数超过一半的元素",
    },
]

answer = """
```python
def majority_element(nums):
    count = {}
    for num in nums:
        if num in count:
            count[num] += 1
        else:
            count[num] = 1

        if count[num] > len(nums) // 2:
            return num

    return None
```
"""
