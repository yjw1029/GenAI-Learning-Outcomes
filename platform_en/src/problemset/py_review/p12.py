description = """
## Count Positives in List
Write a function `count_positives(nums)` that takes a list of numbers `nums` and returns the count of positive numbers in the list. (2 pts)
"""

title = "Count Positives in List (2 pts)"
score = 2

knowledge = ["list", "loop"]

code_template = """
def count_positives(nums):
    # your code
    return ...
"""

code_entrypoint = "count_positives"

validcases = [
    {
        "input": [[1, -4, 0, 5, 3]],
        "output": 3,
        "comment": "Positives are 1, 5, 3, total 3",
    },
]

testcases = [
    *validcases,
    # common cases
    {"input": [[-1, -2, -3, -4]], "output": 0, "comment": "No positive numbers"},
    {"input": [[0, 0, 0, 0]], "output": 0, "comment": "No positive numbers, only 0"},
    {
        "input": [[5, 12, 2, 9]],
        "output": 4,
        "comment": "Positives are 5, 12, 2, 9, total 4",
    },
    {
        "input": [[-5, 3, -2, 1, 0]],
        "output": 2,
        "comment": "Positives are 3, 1, total 2",
    },
    {"input": [[1]], "output": 1, "comment": "Only one positive number 1"},
    {"input": [[-1, 0, 1]], "output": 1, "comment": "Positives are 1, total 1"},
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
