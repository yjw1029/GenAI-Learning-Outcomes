description = """
## Remove List Elements
Given a list `nums` and a value `val`, remove all elements equal to `val` and return the resulting list. The order of elements should not change. (3 pts)
"""

title = "Remove List Elements (3 pts)"
score = 3

knowledge = ["list", "condition", "loop"]

code_template = """
def remove_elements(nums, val):
    # your code
    return ...
"""

code_entrypoint = "remove_elements"

validcases = [
    {"input": [[3, 2, 2, 3], 3], "output": [2, 2], "comment": "Remove all elements equal to 3"},
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [[1, 2, 3, 4, 5], 3],
        "output": [1, 2, 4, 5],
        "comment": "Remove one middle value",
    },
    {"input": [[5, 5, 5, 5], 5], "output": [], "comment": "Remove all elements"},
    {"input": [[1, 2, 3], 4], "output": [1, 2, 3], "comment": "No elements removed"},
    {"input": [[], 1], "output": [], "comment": "Empty list"},
    {"input": [[2, 3, 3, 2, 4], 3], "output": [2, 2, 4], "comment": "Remove multiple consecutive elements"},
    {"input": [[1, 2, 2, 1], 2], "output": [1, 1], "comment": "Remove multiple non-consecutive elements"},
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
