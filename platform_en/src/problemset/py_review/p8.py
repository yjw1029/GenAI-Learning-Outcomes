description = """
## Count Greater Than
Write a function `count_greater_than` that takes an integer list `lst` and an integer `val`, and counts how many values in the list are strictly greater than `val`. (2 pts)
"""

title = "Count Greater Than (2 pts)"
score = 2

knowledge = ["list", "loop", "condition"]

code_template = """
def count_greater_than(lst, val):
    # your code
    return ...
"""

code_entrypoint = "count_greater_than"

validcases = [
    {"input": [[-1, -2, -3, -4], 0], "output": 0, "comment": "No elements greater than 0"},
    {
        "input": [[1, 2, 3, 4], 2],
        "output": 2,
        "comment": "Two elements (3 and 4) are greater than 2",
    },
]

testcases = [
    *validcases,
    # common cases
    {"input": [[5, 6, 7, 8], 7], "output": 1, "comment": "One element (8) is greater than 7"},
    {
        "input": [[10, 20, 30, 40], 25],
        "output": 2,
        "comment": "Two elements (30 and 40) are greater than 25",
    },
    {"input": [[0, 0, 0, 0], 0], "output": 0, "comment": "No elements greater than 0"},
    {
        "input": [[-5, -4, -3, -2, -1], -3],
        "output": 2,
        "comment": "Two elements (-2 and -1) are greater than -3",
    },
    {"input": [[1, 1, 1, 1], 1], "output": 0, "comment": "No elements greater than 1"},
    {"input": [[], 5], "output": 0, "comment": "Empty list has no elements greater than 5"},
]

answer = """
```Python
def count_greater_than(lst, val):
    count = 0
    for num in lst:
        if num > val:
            count += 1
    return count
```
"""
