description = """
## Count Until Break
Write a function `count_until_break(nums)` that takes an integer list `nums`. The function should count elements until it encounters a `0`, then stop and return the count. (3 pts)
"""

title = "Count Until Break (3 pts)"
score = 3

knowledge = ["list", "loop"]

code_template = """
def count_until_break(nums):
    # your code
    return ...
"""

code_entrypoint = "count_until_break"

validcases = [
    {
        "input": [[1, 2, 3, 0, 4, 5]],
        "output": 3,
        "comment": "Before 0, there are 3 elements",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [[5, 4, 3, 2, 1, 0]],
        "output": 5,
        "comment": "Before 0, there are 5 elements",
    },
    {"input": [[0, 1, 2, 3, 4]], "output": 0, "comment": "First element is 0"},
    {"input": [[1, 2, 3, 4, 5]], "output": 5, "comment": "No 0 in list, count all elements"},
    {
        "input": [[-1, -2, 0, 1, 2]],
        "output": 2,
        "comment": "Before 0, there are 2 negative elements",
    },
    {"input": [[0]], "output": 0, "comment": "Single element list, and it is 0"},
    {"input": [[1, 0, 0, 0]], "output": 1, "comment": "Stop counting after the first 0"},
]

answer = """
```Python
def count_until_break(nums):
    count = 0
    for num in nums:
        if num == 0:
            break
        count += 1
    return count
```
"""
