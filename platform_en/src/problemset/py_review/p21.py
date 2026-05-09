description = """
## Sum of Integer Divisions
Write a function `sum_of_divisions(nums, divisor)` that takes a list of numbers `nums` and an integer `divisor`. Return the sum of each element divided by `divisor`, taking only the integer part. (3 pts)
"""

title = "Sum of Integer Divisions (3 pts)"
score = 3

knowledge = ["list", "loop", "number"]

code_template = """
def sum_of_divisions(nums, divisor):
    # your code
    return ...
"""

code_entrypoint = "sum_of_divisions"

validcases = [
    {
        "input": [[20, 15, 30, 45], 10],
        "output": 10,
        "comment": "Result is 2 + 1 + 3 + 4 = 10",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [[10, 20, 30], 5],
        "output": 12,
        "comment": "10/5 + 20/5 + 30/5 = 2 + 4 + 6 = 12",
    },
    {
        "input": [[100, 55, 70, 25], 25],
        "output": 9,
        "comment": "100/25 + 55/25 + 70/25 + 25/25 = 4 + 2 + 2 + 1 = 9",
    },
    {
        "input": [[1, 2, 3, 4, 5], 1],
        "output": 15,
        "comment": "1/1 + 2/1 + 3/1 + 4/1 + 5/1 = 15",
    },
    {
        "input": [[40, 60, 80], 20],
        "output": 9,
        "comment": "40/20 + 60/20 + 80/20 = 2 + 3 + 4 = 9",
    },
    {
        "input": [[5, 10, 15], 10],
        "output": 2,
        "comment": "5/10 + 10/10 + 15/10 = 0 + 1 + 1 = 2",
    },
    {
        "input": [[7, 14, 21], 7],
        "output": 6,
        "comment": "7/7 + 14/7 + 21/7 = 1 + 2 + 3 = 6",
    },
]

answer = """
```Python
def sum_of_divisions(nums, divisor):
    total = 0
    for num in nums:
        total += num // divisor
    return total
```
"""
