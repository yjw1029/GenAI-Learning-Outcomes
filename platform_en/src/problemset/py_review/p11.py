description = """
## Sum of Even Numbers
Write a function `sum_even(nums)` that takes a list of numbers `nums` and returns the sum of all even numbers in the list. (2 pts)
"""

title = "Sum of Even Numbers (2 pts)"
score = 2

knowledge = ["list", "loop"]

code_template = """
def sum_even(nums):
    # your code
    return ...
"""

code_entrypoint = "sum_even"

validcases = [
    {"input": [[1, 2, 3, 4]], "output": 6, "comment": "Even sum is 2 + 4 = 6"},
]

testcases = [
    *validcases,
    # common cases
    {"input": [[5, 7, 8]], "output": 8, "comment": "Even sum is 8"},
    {
        "input": [[10, 20, 30]],
        "output": 60,
        "comment": "Even sum is 10 + 20 + 30 = 60",
    },
    {"input": [[1, 3, 5]], "output": 0, "comment": "No even numbers, sum is 0"},
    {
        "input": [[2, 4, 6, 8]],
        "output": 20,
        "comment": "Even sum is 2 + 4 + 6 + 8 = 20",
    },
    {
        "input": [[-2, -4, -6]],
        "output": -12,
        "comment": "Even negatives sum to -2 + -4 + -6 = -12",
    },
    {"input": [[0, 1, 2]], "output": 2, "comment": "Includes 0 and even 2, sum is 2"},
]

answer = """
```Python
def sum_even(nums):
    total = 0
    for num in nums:
        if num % 2 == 0:
            total += num
    return total
```
"""
