description = """
## Find Missing Number
Given a list of n distinct numbers from 0 to n with one missing, write `find_missing_number(nums)` to return the missing number. (4 pts)
"""

title = "Find Missing Number (4 pts)"
score = 4

knowledge = ["list", "number"]

code_template = """
def find_missing_number(nums):
    # your code
    return ...
"""

code_entrypoint = "find_missing_number"

validcases = [
    {"input": [[0, 3, 7, 1, 2, 8, 4, 5]], "output": 6, "comment": "Missing number between 0 and 8 is 6"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [[0, 1, 2, 4, 5]], "output": 3, "comment": "Missing number between 0 and 5 is 3"},
    {"input": [[1, 2, 3, 4, 5]], "output": 0, "comment": "Missing number between 0 and 5 is 0"},
    {"input": [[0]], "output": 1, "comment": "Missing number between 0 and 1 is 1"},
    {
        "input": [[0, 1, 2, 3, 4, 5, 6, 7, 8]],
        "output": 9,
        "comment": "Missing number between 0 and 9 is 9",
    },
    {"input": [[5, 3, 1, 2, 4, 0, 7]], "output": 6, "comment": "Missing number between 0 and 7 is 6"},
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
