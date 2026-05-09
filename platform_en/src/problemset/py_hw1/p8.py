description = """
## Minimum Score Difference
Given a 0-indexed integer list `nums` where `nums[i]` is the score of student i, and an integer `k`, write `min_difference(nums, k)` to pick any `k` scores so the max-min difference is minimized. Return this minimum difference. (5 pts)

Tip: Use `nums.sort()` to sort a list. For example,
```python
nums = [1, 3, 2, 4]
nums.sort()
print(nums) # [1, 2, 3, 4]
```

Note: `sort` returns `None`.
"""

title = "Minimum Score Difference (5 pts)"
score = 5

code_template = """
def min_difference(nums, k):
    # your code
    return ...
"""

knowledge = ["number", "list", "loop", "condition", "bool"]

code_entrypoint = "min_difference"

validcases = [
    {
        "input": [[30, 55, 70, 85, 50], 3],
        "output": 20,
        "comment": "Choose [55, 50, 70]; max-min difference is 20",
    },
]

testcases = [
    *validcases,
    {
        "input": [[45, 70, 85, 32, 60], 2],
        "output": 10,
        "comment": "Choose [70, 60]; difference is 10",
    },
    {
        "input": [[100, 95, 90, 85, 80], 4],
        "output": 15,
        "comment": "Choose [95, 90, 85, 80]; max-min difference is 15",
    },
    {
        "input": [[22, 27, 23, 25, 24], 5],
        "output": 5,
        "comment": "Subarray covers entire list; difference is 5",
    },
    {
        "input": [[77, 77, 77, 77, 77], 3],
        "output": 0,
        "comment": "All scores equal; difference is 0",
    },
    {
        "input": [[60], 1],
        "output": 0,
        "comment": "Single-element list; difference is 0",
    },
    {
        "input": [[33, 67, 90, 45, 21], 2],
        "output": 12,
        "comment": "Minimum difference occurs in [33, 21]; difference is 12",
    },
]

answer = """
```Python
def min_difference(nums, k):
    # If k <= 1 or nums is empty, the minimum difference is 0
    if k <= 1 or not nums:
        return 0

    # Sort nums
    nums.sort()

    # Initialize minimum difference
    min_diff = None

    # Traverse to find minimum difference among any k consecutive numbers
    for i in range(len(nums) - k + 1):
        diff = nums[i + k - 1] - nums[i]
        if min_diff is None:
            min_diff = diff
        else:
            if diff < min_diff:
                min_diff = diff
    return min_diff
```
"""
