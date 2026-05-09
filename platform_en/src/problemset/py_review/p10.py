description = """
## Generate Star Strings
Write a function `make_star_strings(nums)` that takes a list of non-negative integers `nums` and returns a list of strings made of asterisks (*). Each string should contain as many asterisks as the corresponding number. Note that 0 should produce an empty string. (2 pts)
"""

title = "Generate Star Strings (2 pts)"
score = 2

knowledge = ["list", "string"]

code_template = """
def make_star_strings(nums):
    # your code
    return ...
"""

code_entrypoint = "make_star_strings"

validcases = [
    {
        "input": [[2, 1, 3, 0]],
        "output": ["**", "*", "***", ""],
        "comment": "Each number maps to that many stars; 0 maps to empty string",
    },
]

testcases = [
    *validcases,
    # common cases
    {
        "input": [[5, 2, 0, 1]],
        "output": ["*****", "**", "", "*"],
        "comment": "Star counts correspond to 5, 2, 0, 1",
    },
    {
        "input": [[0, 0, 0]],
        "output": ["", "", ""],
        "comment": "All-zero list returns empty strings",
    },
    {
        "input": [[1, 1, 1, 1]],
        "output": ["*", "*", "*", "*"],
        "comment": "Each number is 1, return one-star strings",
    },
    {
        "input": [[10]],
        "output": ["**********"],
        "comment": "Single number 10 returns a 10-star string",
    },
    {
        "input": [[4, 0, 5]],
        "output": ["****", "", "*****"],
        "comment": "Includes 0 and other numbers, returns correct stars and empty string",
    },
]

answer = """
```Python
def make_star_strings(nums):
    nl = []
    for i in nums:
        nl.append("*" * i)
    return nl
```
"""
